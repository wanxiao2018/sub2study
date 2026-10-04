from setuptools import setup, find_packages

setup(
    name="sub2study",
    version="1.0.0",
    description="Turn YouTube video subtitles into publication-grade bilingual study guides.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="sub2study Contributors",
    url="https://github.com/your-username/sub2study",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2024.8.0",
    ],
    entry_points={
        "console_scripts": [
            "sub2study=sub2study.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
)
