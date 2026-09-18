"""JSON Schema definitions for workflow definitions."""
from typing import Any, Dict

# JSON Schema for validating generated workflow definitions
WORKFLOW_DEFINITION_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "trigger", "steps"],
    "additionalProperties": True,
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "description": "Human-readable workflow name",
        },
        "description": {
            "type": "string",
            "maxLength": 500,
            "description": "Optional workflow description",
        },
        "trigger": {
            "type": "object",
            "required": ["type"],
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["manual", "scheduled", "event"],
                },
                "schedule": {
                    "type": "string",
                    "description": "Cron expression for scheduled triggers",
                },
                "event_type": {
                    "type": "string",
                    "description": "Event type for event triggers",
                },
            },
        },
        "inputs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Required inputs for the workflow",
        },
        "steps": {
            "type": "array",
            "minItems": 1,
            "maxItems": 50,
            "items": {
                "type": "object",
                "required": ["tool"],
                "additionalProperties": True,
                "properties": {
                    "tool": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Tool name to execute",
                    },
                    "input": {
                        "type": "object",
                        "description": "Step input parameters",
                    },
                    "condition": {
                        "type": "string",
                        "description": "Optional conditional expression",
                    },
                },
            },
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name"],
                "additionalProperties": True,
                "properties": {
                    "name": {"type": "string"},
                    "requires_approval": {"type": "boolean"},
                    "tool": {"type": "string"},
                },
            },
        },
        "allowed_tools": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Tools the agent is permitted to use",
        },
        "allowed_resources": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Resources the agent is permitted to access",
        },
    },
}