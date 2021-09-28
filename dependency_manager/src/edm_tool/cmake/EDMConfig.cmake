cmake_minimum_required(VERSION 3.14 FATAL_ERROR)

message("##### Hello there from EVerest dependency manager #####")

find_program(EVEREST_DEPENDENCY_MANAGER "edm")

if(NOT EVEREST_DEPENDENCY_MANAGER)
    message(FATAL_ERROR "Could not find EVerest dependency manager. Please make it available in your PATH.")
endif()

message("Found EVerest dependency manager: ${EVEREST_DEPENDENCY_MANAGER}")

execute_process(
    COMMAND "${EVEREST_DEPENDENCY_MANAGER}" --cmake --working_dir "${PROJECT_SOURCE_DIR}" --out "${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake"
    RESULT_VARIABLE EVEREST_DEPENDENCY_MANAGER_RETURN_CODE
)

if(EVEREST_DEPENDENCY_MANAGER_RETURN_CODE AND NOT EVEREST_DEPENDENCY_MANAGER_RETURN_CODE EQUAL 0)
    message(FATAL_ERROR "EVerest dependency manager did not run successfully.")
endif()

include("${CMAKE_CURRENT_LIST_DIR}/CPM.cmake")
include("${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake")
