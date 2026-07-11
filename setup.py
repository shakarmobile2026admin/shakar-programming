from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="shakar-accounting-system",
    version="1.0.0",
    author="محمدحسین آقازاده",
    author_email="info@shakar.com",
    description="نرم‌افزار حسابداری و مدیریت فروشگاه شاکر",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shakarmobile2026admin/shakar-programming",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Business",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shakar=src.main:main",
        ],
    },
    include_package_data=True,
)