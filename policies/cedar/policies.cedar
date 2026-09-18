// Default Cedar policies for MicroAgent

// Global tenant isolation invariant
// A user can never access a resource that belongs to a different organization
forbid (
    principal,
    action,
    resource
)
when {
    resource has organization_id && principal.organization_id != resource.organization_id
};

// Owner has full access to their organization
permit (
    principal,
    action,
    resource
)
when {
    principal.role == "owner"
};

// Execution policy
permit (
    principal == User::"system",
    action == Action::"ExecuteTool",
    resource
)
when {
    context.workflow_id != "" // Abstract condition: tool must be registered for workflow
};
