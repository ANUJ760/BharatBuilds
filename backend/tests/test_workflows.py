"""Workflow definition validation tests."""
import pytest

from backend.workflow.validator import WorkflowValidator
from backend.models.workflow import WorkflowDefinition, WorkflowTrigger, WorkflowStep


class TestWorkflowValidator:
    """Test workflow validation logic."""

    @pytest.fixture
    def validator(self):
        return WorkflowValidator()

    @pytest.fixture
    def valid_definition(self):
        return WorkflowDefinition(
            name="test_workflow",
            trigger=WorkflowTrigger(type="manual"),
            steps=[
                WorkflowStep(tool="test_tool", input={}),
            ],
            allowed_tools=["test_tool"],
        )

    def test_valid_workflow(self, validator, valid_definition):
        validator.validate(valid_definition)

    def test_empty_allowed_tools_raises(self, validator, valid_definition):
        valid_definition.allowed_tools = []
        with pytest.raises(Exception):
            validator.validate(valid_definition)
