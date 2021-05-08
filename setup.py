import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PNEEv2", # Replace with your own username
    version="0.0.1",
    author="megamaz",
    author_email="raphael.mazuel@gmail.com",
    description="An improved version of PNEE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/megamaz/PythonNoodleExtensionsEditorV2",
    project_urls={
        "Bug Tracker": "https://github.com/megamaz/PythonNoodleExtensionsEditorV2/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    packages=setuptools.find_packages("."),
    install_requires=[
        "tqdm"
    ]

)