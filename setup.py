from setuptools import setup, find_packages

setup(
    name="jobtrack",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "supabase==2.0.3",
        "python-jose==3.3.0",
        "bcrypt==3.2.2",
        "python-multipart==0.0.6",
        "pydantic[email]==2.4.2",
        "pydantic-settings==2.0.3",
        "python-dotenv==1.0.0",
    ],
)
