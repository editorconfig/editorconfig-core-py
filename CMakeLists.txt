# This file is used for testing only

# To perform the test, run `cmake .` at the root of the project tree followed
# by ctest .

cmake_minimum_required(VERSION 3.16.3)

# Do not check any compiler
project(editorconfig-core-py NONE)

find_package(PythonInterp)

if(NOT PYTHONINTERP_FOUND)
    message(FATAL_ERROR
        "Python interpreter is not found. If you have python installed, please run:
        cmake -DPYTHON_EXECUTABLE=/path/to/python .")
endif()

enable_testing()
set(EDITORCONFIG_CMD ${PYTHON_EXECUTABLE} -m editorconfig)
add_subdirectory(tests)
