from setuptools import setup, find_packages #type:ignore

def parse_requirements(filename):
    with open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="extracao_monday",
    version="0.2.1",
    description="Biblioteca para automação de extração e importação no Monday.com.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gustavo Nery",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
    python_requires=">=3.11",
)
