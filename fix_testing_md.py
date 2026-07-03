from hermes_tools import patch
patch(
    path="docs/TESTING.md",
    old_string="""### Workflow Triggers
- Push to  branch.
- Pull requests to  branch.
- Weekly schedules.""",
    new_string="""### Workflow Triggers
- : Push to  branch and pull requests to  branch.
- : Weekly schedules and manual ."""
)
