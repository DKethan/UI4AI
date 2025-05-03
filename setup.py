from setuptools import setup, find_packages

setup(
    name="UI4AI",
    version="0.1.2",
    author="Kethan Dosapati",
    description="A Streamlit UI for LLM chat applications with persistence and chat history",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DKethan/UI4AI/tree/dev-01",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    keywords="streamlit, chat, ui, llm, chatbot, conversation, ai, openai, UI4AI, UI4AI PYPI, UI4AI package",
    python_requires='>=3.7',
)