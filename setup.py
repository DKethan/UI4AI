from setuptools import setup, find_packages

setup(
    name="UI4AI",
    version="0.1.0",
    author="Robin",
    description="Streamlit UI for LLM chat apps",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DKethan/UI4AI/tree/dev-01",
    packages=find_packages(),
    install_requires=["streamlit"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
