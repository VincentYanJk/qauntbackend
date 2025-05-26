from setuptools import setup, find_packages

setup(
    name="gptquant",
    version="0.1.0",
    description="Professional BTC Quant Trading Framework",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "backtrader",
        "pandas",
        "numpy",
        "matplotlib",
        "scikit-learn",
        "xgboost",
        "torch",
        "python-binance",
        "nbformat"
    ],
    include_package_data=True,
    zip_safe=False
)