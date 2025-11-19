from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "pcbridge",          # Python module name
        ["test.cpp"],        # C++ source file
        cxx_std=17,
    )
]

setup(
    name="pcbridge",
    version="0.1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=["pybind11"],
)