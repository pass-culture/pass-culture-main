from setuptools import setup


setup(
    name="PcCommitizen",
    version="0.1.0",
    py_modules=["pc_jira"],
    license="MIT",
    long_description="A custom commitizen configuration to load from jira",
    install_requires=["commitizen"],
    entry_points={"commitizen.plugin": ["pc_jira = pc_jira:PcJiraCz"]},
)
