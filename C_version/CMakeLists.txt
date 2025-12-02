cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
project(Cforge)

set(CMAKE_CXX_STANDARD 17)

# 关键修改：使用 execute_process 动态获取 PyTorch 的 CMake 路径
execute_process(
    COMMAND python -c "import torch; print(torch.utils.cmake_prefix_path)"
    OUTPUT_VARIABLE Torch_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Found Torch at: ${Torch_DIR}")
set(CMAKE_PREFIX_PATH "${Torch_DIR}")

find_package(Torch REQUIRED)
add_executable(a.out main.cpp)
target_link_libraries(a.out "${TORCH_LIBRARIES}")