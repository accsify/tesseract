cmake_minimum_required(VERSION 3.20)

# CMake 3.31+ compatibility: allow legacy subprojects (e.g. leptonica) requiring CMake < 3.5
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum policy version for subprojects" FORCE)

# Read canonical project version from VERSION file
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION")
    file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" RAW_VERSION LIMIT_COUNT 1)
    string(STRIP "${RAW_VERSION}" ACCSIFY_PROJECT_VERSION)
else()
    set(ACCSIFY_PROJECT_VERSION "1.0.5.1")
endif()

project(accsify_tesseract_engine
    VERSION ${ACCSIFY_PROJECT_VERSION}
    LANGUAGES C CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

# -----------------------------------------------------------------------------
# Static Runtime (/MT) Configuration - Guarantees ZERO External C-Runtime DLLs
# -----------------------------------------------------------------------------
if(MSVC)
    cmake_policy(SET CMP0091 NEW)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    set(WIN32_MT_BUILD ON CACHE BOOL "Force MT runtime for Tesseract" FORCE)
endif()

# Global settings for embedded dependencies
set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build static dependencies" FORCE)

# -----------------------------------------------------------------------------
# 1. Leptonica Configuration (Static)
# -----------------------------------------------------------------------------
set(SW_BUILD OFF CACHE BOOL "" FORCE)
set(BUILD_PROG OFF CACHE BOOL "" FORCE)
set(ENABLE_ZLIB OFF CACHE BOOL "" FORCE)
set(ENABLE_PNG OFF CACHE BOOL "" FORCE)
set(ENABLE_JPEG OFF CACHE BOOL "" FORCE)
set(ENABLE_TIFF OFF CACHE BOOL "" FORCE)
set(ENABLE_GIF OFF CACHE BOOL "" FORCE)
set(ENABLE_WEBP OFF CACHE BOOL "" FORCE)
set(ENABLE_OPENJPEG OFF CACHE BOOL "" FORCE)

add_subdirectory(deps/leptonica ${CMAKE_BINARY_DIR}/leptonica EXCLUDE_FROM_ALL)

# Provide in-tree LeptonicaConfig.cmake for Tesseract find_package(Leptonica CONFIG)
file(WRITE "${CMAKE_BINARY_DIR}/leptonica/LeptonicaConfig.cmake" "
set(Leptonica_VERSION \"1.84.1\")
set(Leptonica_VERSION_MAJOR 1)
set(Leptonica_VERSION_MINOR 84)
set(Leptonica_VERSION_PATCH 1)
set(Leptonica_INCLUDE_DIRS \"${CMAKE_CURRENT_SOURCE_DIR}/deps/leptonica/src;${CMAKE_BINARY_DIR}/leptonica/src\")
set(Leptonica_LIBRARIES leptonica)
")

# Pass built Leptonica to Tesseract
set(Leptonica_DIR "${CMAKE_BINARY_DIR}/leptonica" CACHE PATH "" FORCE)
set(Leptonica_FOUND TRUE CACHE BOOL "" FORCE)
set(Leptonica_LIBRARIES leptonica CACHE STRING "" FORCE)
set(Leptonica_INCLUDE_DIRS
    "${CMAKE_CURRENT_SOURCE_DIR}/deps/leptonica/src"
    "${CMAKE_BINARY_DIR}/leptonica/src"
    CACHE PATH "" FORCE
)

# -----------------------------------------------------------------------------
# 2. Tesseract Configuration (Static)
# -----------------------------------------------------------------------------
set(BUILD_TRAINING_TOOLS OFF CACHE BOOL "Disable training tools" FORCE)
set(BUILD_TESTS OFF CACHE BOOL "Disable tests" FORCE)
set(GRAPHICS_DISABLED ON CACHE BOOL "Disable ScrollView graphics" FORCE)
set(DISABLE_CURL ON CACHE BOOL "Disable libcurl" FORCE)
set(DISABLE_ARCHIVE ON CACHE BOOL "Disable libarchive" FORCE)
set(DISABLE_TIFF ON CACHE BOOL "Disable libtiff" FORCE)
set(OPENMP_BUILD OFF CACHE BOOL "Disable OpenMP" FORCE)
set(INSTALL_CONFIGS OFF CACHE BOOL "Disable configs install" FORCE)

add_subdirectory(deps/tesseract ${CMAKE_BINARY_DIR}/tesseract EXCLUDE_FROM_ALL)

# Ensure static flags on libtesseract target
if(TARGET libtesseract)
    set_target_properties(libtesseract PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
    )
endif()
if(TARGET leptonica)
    set_target_properties(leptonica PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
    )
endif()

# -----------------------------------------------------------------------------
# 3. Accsi Monolithic Tesseract Engine DLL (tesseract_engine.dll)
# -----------------------------------------------------------------------------
set(TESS_ENGINE_SOURCES
    src/dllmain.cpp
    src/engine_api.cpp
    src/model_manager.cpp
    src/downloader_winhttp.cpp
    version.rc
)

add_library(tesseract_engine SHARED ${TESS_ENGINE_SOURCES})

set_target_properties(tesseract_engine PROPERTIES
    OUTPUT_NAME "tesseract_engine"
    PREFIX ""
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)

target_compile_definitions(tesseract_engine PRIVATE
    TESSERACT_ENGINE_EXPORTS
    TESS_STATIC
    LEPT_STATIC
    WIN32_LEAN_AND_MEAN
    NOMINMAX
    _CRT_SECURE_NO_WARNINGS
)

target_include_directories(tesseract_engine PRIVATE
    include
    src
    deps/tesseract/include
    deps/tesseract/src
    deps/leptonica/src
    ${CMAKE_BINARY_DIR}/leptonica/src
    ${CMAKE_BINARY_DIR}/tesseract/include
)

target_link_libraries(tesseract_engine PRIVATE
    libtesseract
    leptonica
    winhttp
    ws2_32
    shlwapi
    user32
)

# Output directories
set_target_properties(tesseract_engine PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/$<IF:$<EQUAL:${CMAKE_SIZEOF_VOID_P},8>,x64,x86>"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/$<IF:$<EQUAL:${CMAKE_SIZEOF_VOID_P},8>,x64,x86>"
)

# -----------------------------------------------------------------------------
# 4. Accsify Tesseract CLI Executable (tesseract_cli.exe)
# -----------------------------------------------------------------------------
add_executable(tesseract_cli src/cli_main.cpp)

set_target_properties(tesseract_cli PROPERTIES
    OUTPUT_NAME "tesseract_cli"
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin/$<IF:$<EQUAL:${CMAKE_SIZEOF_VOID_P},8>,x64,x86>"
)

target_include_directories(tesseract_cli PRIVATE
    include
    src
)

target_link_libraries(tesseract_cli PRIVATE
    tesseract_engine
)

