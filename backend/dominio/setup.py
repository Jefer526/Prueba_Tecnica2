"""
Setup.py para el paquete del dominio
Alternativa a Poetry para instalación con pip
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lite-thinking-dominio",
    version="1.0.0",
    author="Jeffer Niño",
    author_email="jeffer.nino@example.com",
    description="Capa de Dominio - Sistema de Gestión de Inventario (Clean Architecture)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/lite-thinking-dominio",
    packages=find_packages(include=['entidades', 'entidades.*', 'excepciones', 'excepciones.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Sin dependencias - Dominio puro
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
)
