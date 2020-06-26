import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as r:
    requirements = r.readlines()

setuptools.setup(
    name="deep_poop",  # Replace with your own username
    version="0.0.1",
    author="Karl Gylleus",
    author_email="karl.gylleus@gmail.com",
    description="YTP video generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[requirements],
    python_requires=">=3.6",
)
