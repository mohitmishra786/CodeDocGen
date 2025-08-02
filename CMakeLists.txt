cmake_minimum_required(VERSION 3.14)
project(CodeDocGen VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/cpp_parser.cpp
    src/documentation_generator.cpp
    src/ast_analyzer.cpp
)

# Header files
set(HEADERS
    include/cpp_parser.h
    include/documentation_generator.h
    include/ast_analyzer.h
)

# Create library
add_library(codedocgen_cpp SHARED ${SOURCES} ${HEADERS})

# Set library properties
set_target_properties(codedocgen_cpp PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER "${HEADERS}"
)

# Install rules
install(TARGETS codedocgen_cpp
    EXPORT CodeDocGenTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    PUBLIC_HEADER DESTINATION include
)

# Install headers
install(DIRECTORY include/ DESTINATION include)

# Export targets
install(EXPORT CodeDocGenTargets
    FILE CodeDocGenTargets.cmake
    NAMESPACE CodeDocGen::
    DESTINATION lib/cmake/CodeDocGen
)

# Create config file
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    CodeDocGenConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Install config files
install(FILES
    cmake/CodeDocGenConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/CodeDocGenConfigVersion.cmake
    DESTINATION lib/cmake/CodeDocGen
)

# Create pkg-config file
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/codedocgen.pc.in
    ${CMAKE_CURRENT_BINARY_DIR}/codedocgen.pc
    @ONLY
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/codedocgen.pc
    DESTINATION lib/pkgconfig
) 