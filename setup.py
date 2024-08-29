from setuptools import find_packages, setup

setup(
    name="ratehttp",
    version="0.1.3",
    author="Shark",
    author_email="shark.wangl@gmail.com",
    description="ratehttp is fork from octopus-api based on aiohttp, and ratehttp provides ssl-verify setting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dreambe/ratehttp",
    packages=find_packages(),  # 自动发现所有包含 __init__.py 的包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
