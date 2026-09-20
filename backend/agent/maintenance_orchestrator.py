"""Maintenance Orchestrator for BharatBuilds.

Orchestrates the complete autonomous maintenance lifecycle:
Detection → Diagnosis → Repair → Local Candidate Verification → Candidate Lambda Deployment
→ Synthetic Health Probe → Production Promotion / Rejection.

Tracks job state, enforces attempt boundaries (max 2), and records all events
to the DynamoDB Decision Timeline.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from backend.agent.candidate_verifier import verify_candidate_code
from backend.agent.health_probe import DEFAULT_TIMEOUT_SECONDS, probe_url
from backend.agent.repair import (
    BedrockCodeRepairProvider,
    CodeRepairProvider,
)
from backend.agent.safety_guards import AppConcurrencyLock, sanitize_issue
from backend.agent.trace_logger import get_timeline, log_step
from backend.deploy.lambda_deployer import (
    deploy_candidate_to_lambda,
    promote_candidate_to_prod,
)
from backend.models.app import (
    CandidateDeploymentResult,
    CandidateVerificationResult,
    HealthCheckResult,
    MaintenanceIssue,
    MaintenanceJob,
    MaintenanceResult,
    MaintenanceStatus,
    PromotionResult,
    RepairResult,
    StepStatus,
    StepType,
    TimelineStep,
)

logger = logging.getLogger(__name__)

MAX_REPAIR_ATTEMPTS = 2


class MaintenanceOrchestrator:
    """Orchestrates diagnosis, repair, candidate deployment, health verification, and production promotion."""

    def __init__(
        self,
        *,
        repair_provider: CodeRepairProvider | None = None,
        model_id: str = "",
        region: str = "ap-south-1",
        table_name: str = "",
        function_name: str = "",
        max_attempts: int = MAX_REPAIR_ATTEMPTS,
        probe_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        candidate_deployer: Callable[..., Any] | None = None,
        candidate_promoter: Callable[..., Any] | None = None,
        health_prober: Callable[..., Any] | None = None,
    ) -> None:
        self.repair_provider = repair_provider or BedrockCodeRepairProvider(
            model_id=model_id,
            region=region,
        )
        self.model_id = model_id
        self.region = region
        self.table_name = table_name
        self.function_name = function_name
        self.max_attempts = max_attempts
        self.probe_timeout_seconds = probe_timeout_seconds
        self.candidate_deployer = candidate_deployer or deploy_candidate_to_lambda
        self.candidate_promoter = candidate_promoter or promote_candidate_to_prod
        self.health_prober = health_prober or probe_url

    async def run_maintenance(
        self,
        app_id: str,
        issue: MaintenanceIssue,
        *,
        existing_code: str | None = None,
        persist_timeline: bool = True,
    ) -> MaintenanceResult:
        """Run the maintenance pipeline for a detected issue.

        Parameters
        ----------
        app_id:
            The unique identifier of the app under maintenance.
        issue:
            The detected error details.
        existing_code:
            Optional direct source code of the current app. If omitted,
            fetched automatically from the app's timeline.
        persist_timeline:
            Whether to write timeline steps to DynamoDB (defaults to True).

        Returns
        -------
        MaintenanceResult
            Structured report with diagnostic analysis, candidate code, verification results,
            deployment & health check outcome, and final job status.
        """
        # 1. Sanitize untrusted input fields
        sanitized_issue = sanitize_issue(issue)

        # 2. Acquire concurrency lock
        acquired = await AppConcurrencyLock.acquire(app_id)
        if not acquired:
            conflict_msg = f"Concurrent maintenance job already in progress for app {app_id}"
            logger.warning("Maintenance rejected: %s", conflict_msg)
            job = MaintenanceJob(app_id=app_id, issue=sanitized_issue, status=MaintenanceStatus.REJECTED)
            job.summary = conflict_msg
            reject_step = TimelineStep(
                app_id=app_id,
                step_type=StepType.MAINTENANCE_REJECT,
                status=StepStatus.ERROR,
                reasoning=conflict_msg,
                error_message=conflict_msg,
            )
            if persist_timeline:
                await log_step(reject_step, table_name=self.table_name, region=self.region)
            return MaintenanceResult(
                job=job,
                status=MaintenanceStatus.REJECTED,
                summary=conflict_msg,
                timeline_steps=[reject_step],
            )

        try:
            return await self._execute_maintenance_workflow(
                app_id,
                sanitized_issue,
                existing_code=existing_code,
                persist_timeline=persist_timeline,
            )
        finally:
            await AppConcurrencyLock.release(app_id)

    async def _execute_maintenance_workflow(
        self,
        app_id: str,
        issue: MaintenanceIssue,
        *,
        existing_code: str | None = None,
        persist_timeline: bool = True,
    ) -> MaintenanceResult:
        job = MaintenanceJob(app_id=app_id, issue=issue, status=MaintenanceStatus.PENDING)
        timeline_steps: list[TimelineStep] = []
        parent_step_id: str | None = None

        # 1. Resolve existing code
        current_code = existing_code
        if not current_code:
            try:
                timeline = await get_timeline(
                    app_id,
                    table_name=self.table_name,
                    region=self.region,
                )
                for step in reversed(timeline):
                    if step.code_snapshot:
                        current_code = step.code_snapshot
                        parent_step_id = step.step_id
                        break
            except Exception as exc:
                logger.warning("Could not fetch timeline for app %s: %s", app_id, exc)

        if not current_code:
            err_msg = f"No existing code snapshot found for app {app_id}"
            logger.error(err_msg)
            job.status = MaintenanceStatus.FAILED
            job.summary = err_msg

            reject_step = TimelineStep(
                app_id=app_id,
                parent_step_id=parent_step_id,
                step_type=StepType.MAINTENANCE_REJECT,
                status=StepStatus.ERROR,
                error_message=err_msg,
                reasoning=err_msg,
            )
            timeline_steps.append(reject_step)
            if persist_timeline:
                await log_step(reject_step, table_name=self.table_name, region=self.region)

            return MaintenanceResult(
                job=job,
                status=MaintenanceStatus.FAILED,
                summary=err_msg,
                timeline_steps=timeline_steps,
            )

        # 2. Record MAINTENANCE_DETECT step
        detect_step = TimelineStep(
            app_id=app_id,
            parent_step_id=parent_step_id,
            step_type=StepType.MAINTENANCE_DETECT,
            input_text=issue.error_message,
            reasoning=f"Detected {issue.issue_type} ({issue.severity}): {issue.error_message}",
            status=StepStatus.OK,
        )
        timeline_steps.append(detect_step)
        parent_step_id = detect_step.step_id
        if persist_timeline:
            await log_step(detect_step, table_name=self.table_name, region=self.region)

        # 3. Diagnostic & Repair loop (up to max_attempts)
        current_issue = issue
        last_repair_result: RepairResult | None = None
        last_verification_result: CandidateVerificationResult | None = None

        for attempt in range(1, self.max_attempts + 1):
            job.attempt_count = attempt
            job.status = MaintenanceStatus.DIAGNOSING
            logger.info("Starting maintenance attempt %d/%d for app %s", attempt, self.max_attempts, app_id)

            # Diagnosis & Patch generation
            repair_result = await self.repair_provider.diagnose_and_repair(current_code, current_issue)
            last_repair_result = repair_result

            if not repair_result.is_success:
                logger.warning("Repair provider failed on attempt %d: %s", attempt, repair_result.error_message)
                diagnose_step = TimelineStep(
                    app_id=app_id,
                    parent_step_id=parent_step_id,
                    step_type=StepType.MAINTENANCE_DIAGNOSE,
                    status=StepStatus.ERROR,
                    error_message=repair_result.error_message,
                    reasoning=f"Diagnosis failed on attempt {attempt}: {repair_result.error_message}",
                )
                timeline_steps.append(diagnose_step)
                if persist_timeline:
                    await log_step(diagnose_step, table_name=self.table_name, region=self.region)

                job.status = MaintenanceStatus.FAILED
                job.summary = f"Diagnosis failed: {repair_result.error_message}"

                reject_step = TimelineStep(
                    app_id=app_id,
                    parent_step_id=diagnose_step.step_id,
                    step_type=StepType.MAINTENANCE_REJECT,
                    status=StepStatus.ERROR,
                    error_message=repair_result.error_message,
                    reasoning=f"Maintenance aborted: {repair_result.error_message}",
                )
                timeline_steps.append(reject_step)
                if persist_timeline:
                    await log_step(reject_step, table_name=self.table_name, region=self.region)

                return MaintenanceResult(
                    job=job,
                    status=MaintenanceStatus.FAILED,
                    diagnosis=repair_result.diagnosis,
                    summary=job.summary,
                    repair_result=repair_result,
                    timeline_steps=timeline_steps,
                )

            # Log DIAGNOSE step
            diagnose_step = TimelineStep(
                app_id=app_id,
                parent_step_id=parent_step_id,
                step_type=StepType.MAINTENANCE_DIAGNOSE,
                reasoning=repair_result.diagnosis,
                status=StepStatus.OK,
            )
            timeline_steps.append(diagnose_step)
            parent_step_id = diagnose_step.step_id
            if persist_timeline:
                await log_step(diagnose_step, table_name=self.table_name, region=self.region)

            # Log PATCH step
            job.status = MaintenanceStatus.PATCHING
            patch_step = TimelineStep(
                app_id=app_id,
                parent_step_id=parent_step_id,
                step_type=StepType.MAINTENANCE_PATCH,
                code_snapshot=repair_result.patched_code,
                code_diff=f"+{len(repair_result.patched_code.splitlines())} lines",
                reasoning=repair_result.summary,
                status=StepStatus.OK,
            )
            timeline_steps.append(patch_step)
            parent_step_id = patch_step.step_id
            job.candidate_step_id = patch_step.step_id
            if persist_timeline:
                await log_step(patch_step, table_name=self.table_name, region=self.region)

            # 4. Candidate verification (Local)
            job.status = MaintenanceStatus.VERIFYING
            verification_result = verify_candidate_code(repair_result.patched_code)
            last_verification_result = verification_result

            if verification_result.passed:
                # Local verification passed
                verify_step = TimelineStep(
                    app_id=app_id,
                    parent_step_id=parent_step_id,
                    step_type=StepType.MAINTENANCE_VERIFY,
                    reasoning=f"Candidate passed all {len(verification_result.checks_passed)} verification checks ({', '.join(verification_result.checks_passed)})",
                    status=StepStatus.OK,
                )
                timeline_steps.append(verify_step)
                parent_step_id = verify_step.step_id
                if persist_timeline:
                    await log_step(verify_step, table_name=self.table_name, region=self.region)

                # 5. Live Candidate Deployment (Isolated from Production)
                try:
                    candidate_deployment: CandidateDeploymentResult = await self.candidate_deployer(
                        app_id,
                        repair_result.patched_code,
                        function_name=self.function_name,
                        region=self.region,
                    )
                except Exception as exc:
                    err_msg = f"Candidate deployment failed: {exc}"
                    logger.error(err_msg)
                    job.status = MaintenanceStatus.FAILED
                    job.summary = err_msg
                    reject_step = TimelineStep(
                        app_id=app_id,
                        parent_step_id=parent_step_id,
                        step_type=StepType.MAINTENANCE_REJECT,
                        status=StepStatus.ERROR,
                        error_message=err_msg,
                        reasoning=f"Candidate deployment failed: {exc}. Production remains untouched.",
                    )
                    timeline_steps.append(reject_step)
                    if persist_timeline:
                        await log_step(reject_step, table_name=self.table_name, region=self.region)
                    return MaintenanceResult(
                        job=job,
                        status=MaintenanceStatus.FAILED,
                        diagnosis=repair_result.diagnosis,
                        summary=job.summary,
                        candidate_code=repair_result.patched_code,
                        repair_result=repair_result,
                        verification_result=verification_result,
                        timeline_steps=timeline_steps,
                    )

                job.candidate_version = candidate_deployment.candidate_version
                job.candidate_url = candidate_deployment.candidate_url

                # 6. Synthetic Health Probe on Candidate Function URL
                logger.info(
                    "Probing candidate Function URL: %s (timeout=%.1fs)",
                    candidate_deployment.candidate_url,
                    self.probe_timeout_seconds,
                )
                health_check_result: HealthCheckResult = await self.health_prober(
                    candidate_deployment.candidate_url,
                    timeout_seconds=self.probe_timeout_seconds,
                )

                if not health_check_result.is_healthy:
                    # Health check failed -> REJECT candidate safely, prod untouched
                    err_detail = health_check_result.error_message or f"HTTP status {health_check_result.status_code}"
                    reject_reason = (
                        f"Candidate health check failed for version {candidate_deployment.candidate_version} "
                        f"at {candidate_deployment.candidate_url} (status={health_check_result.status_code}, "
                        f"latency={health_check_result.latency_ms}ms, error={health_check_result.error_message}). "
                        f"Production alias remains untouched on stable version."
                    )
                    logger.warning("Candidate health check failed for app %s: %s", app_id, err_detail)
                    job.status = MaintenanceStatus.REJECTED
                    job.summary = f"Candidate health check failed on candidate URL {candidate_deployment.candidate_url} (version {candidate_deployment.candidate_version}): {err_detail}"

                    reject_step = TimelineStep(
                        app_id=app_id,
                        parent_step_id=parent_step_id,
                        step_type=StepType.MAINTENANCE_REJECT,
                        status=StepStatus.OK,
                        latency_ms=health_check_result.latency_ms,
                        error_message=health_check_result.error_message,
                        reasoning=reject_reason,
                    )
                    timeline_steps.append(reject_step)
                    if persist_timeline:
                        await log_step(reject_step, table_name=self.table_name, region=self.region)

                    return MaintenanceResult(
                        job=job,
                        status=MaintenanceStatus.REJECTED,
                        diagnosis=repair_result.diagnosis,
                        summary=job.summary,
                        candidate_code=repair_result.patched_code,
                        repair_result=repair_result,
                        verification_result=verification_result,
                        candidate_deployment=candidate_deployment,
                        health_check_result=health_check_result,
                        timeline_steps=timeline_steps,
                    )

                # 7. Health check passed -> Promote candidate to production prod alias
                try:
                    target_func = self.function_name or candidate_deployment.function_name
                    promotion_result: PromotionResult = await self.candidate_promoter(
                        function_name=target_func,
                        candidate_version=candidate_deployment.candidate_version,
                        region=self.region,
                    )
                except Exception as exc:
                    err_msg = f"Promotion failed while updating prod alias to version {candidate_deployment.candidate_version}: {exc}"
                    logger.error(err_msg)
                    job.status = MaintenanceStatus.FAILED
                    job.summary = err_msg
                    reject_step = TimelineStep(
                        app_id=app_id,
                        parent_step_id=parent_step_id,
                        step_type=StepType.MAINTENANCE_REJECT,
                        status=StepStatus.ERROR,
                        error_message=err_msg,
                        reasoning=f"Production promotion failed: {exc}. Candidate version {candidate_deployment.candidate_version} preserved for diagnosis.",
                    )
                    timeline_steps.append(reject_step)
                    if persist_timeline:
                        await log_step(reject_step, table_name=self.table_name, region=self.region)
                    return MaintenanceResult(
                        job=job,
                        status=MaintenanceStatus.FAILED,
                        diagnosis=repair_result.diagnosis,
                        summary=job.summary,
                        candidate_code=repair_result.patched_code,
                        repair_result=repair_result,
                        verification_result=verification_result,
                        candidate_deployment=candidate_deployment,
                        health_check_result=health_check_result,
                        timeline_steps=timeline_steps,
                    )

                # 8. Promotion succeeded
                job.status = MaintenanceStatus.PROMOTED
                job.promoted_version = promotion_result.promoted_version
                job.previous_version = promotion_result.previous_version
                prev_str = promotion_result.previous_version or "initial"
                job.summary = f"Candidate version {promotion_result.promoted_version} passed health checks and promoted to production (replacing version {prev_str})."

                promote_step = TimelineStep(
                    app_id=app_id,
                    parent_step_id=parent_step_id,
                    step_type=StepType.MAINTENANCE_PROMOTE,
                    code_snapshot=repair_result.patched_code,
                    latency_ms=health_check_result.latency_ms,
                    reasoning=(
                        f"Candidate version {promotion_result.promoted_version} passed synthetic health check "
                        f"(status={health_check_result.status_code}, latency={health_check_result.latency_ms}ms) "
                        f"and promoted to production alias 'prod' (previous version: {promotion_result.previous_version or 'none'}). "
                        f"Live URL: {promotion_result.prod_url or candidate_deployment.candidate_url}."
                    ),
                    status=StepStatus.OK,
                )
                timeline_steps.append(promote_step)
                if persist_timeline:
                    await log_step(promote_step, table_name=self.table_name, region=self.region)

                logger.info(
                    "Maintenance succeeded on attempt %d for app %s: version %s promoted to prod (prev: %s)",
                    attempt,
                    app_id,
                    promotion_result.promoted_version,
                    promotion_result.previous_version or "none",
                )
                return MaintenanceResult(
                    job=job,
                    status=MaintenanceStatus.PROMOTED,
                    diagnosis=repair_result.diagnosis,
                    summary=job.summary,
                    candidate_code=repair_result.patched_code,
                    repair_result=repair_result,
                    verification_result=verification_result,
                    candidate_deployment=candidate_deployment,
                    health_check_result=health_check_result,
                    promotion_result=promotion_result,
                    timeline_steps=timeline_steps,
                )

            # Verification failed
            logger.warning("Candidate verification failed on attempt %d: %s", attempt, verification_result.error_message)
            verify_step = TimelineStep(
                app_id=app_id,
                parent_step_id=parent_step_id,
                step_type=StepType.MAINTENANCE_VERIFY,
                status=StepStatus.ERROR,
                error_message=verification_result.error_message,
                reasoning=f"Candidate verification failed on attempt {attempt}: {verification_result.error_message}",
            )
            timeline_steps.append(verify_step)
            parent_step_id = verify_step.step_id
            if persist_timeline:
                await log_step(verify_step, table_name=self.table_name, region=self.region)

            if attempt < self.max_attempts:
                # Augment issue context for retry attempt
                current_issue = MaintenanceIssue(
                    issue_type=issue.issue_type,
                    severity=issue.severity,
                    error_message=(
                        f"{issue.error_message}\n\n"
                        f"Previous repair attempt {attempt} failed verification check:\n"
                        f"{verification_result.error_message}"
                    ),
                    endpoint=issue.endpoint,
                    detection_source="verification_retry",
                )

        # 9. All attempts exhausted and failed -> REJECT candidate safely
        job.status = MaintenanceStatus.REJECTED
        job.summary = f"Candidate rejected after {self.max_attempts} attempts: {last_verification_result.error_message if last_verification_result else 'Verification failed'}"

        reject_step = TimelineStep(
            app_id=app_id,
            parent_step_id=parent_step_id,
            step_type=StepType.MAINTENANCE_REJECT,
            status=StepStatus.OK,
            reasoning=f"Candidate rejected: production remains untouched. {job.summary}",
        )
        timeline_steps.append(reject_step)
        if persist_timeline:
            await log_step(reject_step, table_name=self.table_name, region=self.region)

        logger.warning("Maintenance rejected after %d attempts for app %s", self.max_attempts, app_id)
        return MaintenanceResult(
            job=job,
            status=MaintenanceStatus.REJECTED,
            diagnosis=last_repair_result.diagnosis if last_repair_result else None,
            summary=job.summary,
            candidate_code=last_repair_result.patched_code if last_repair_result else None,
            repair_result=last_repair_result,
            verification_result=last_verification_result,
            timeline_steps=timeline_steps,
        )

