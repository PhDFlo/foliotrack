from setuptools import setup, find_packages

setup(
    name="Portfolio-Manager",
    version="2.0.1",
    description="Tool to keep balance a portfolio of securities while investing.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="PhDFlo",
    url="https://github.com/PhDFlo/Portfolio-Balancer",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pyscipopt",
        "cvxpy",
        "gradio",
        "pandas",
        "matplotlib",
        "pyQt6",
        "yfinance",
        "ecbdata",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
