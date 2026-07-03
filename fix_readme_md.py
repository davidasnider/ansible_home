from hermes_tools import patch
patch(
    path="README.md",
    old_string="""# Or check a specific playbook manually
ansible-playbook --syntax-check -i inventory/hosts.yml site.yml""",
    new_string="""# Or check the master playbook manually
ansible-playbook --syntax-check -i inventory/hosts.yml site.yml"""
)
