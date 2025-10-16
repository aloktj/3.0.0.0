cmake_minimum_required(VERSION 3.16)

list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(TrdpConfigLoader)

set(TRDP_CONFIG "" CACHE STRING "Name of a legacy make configuration file from config/ used to seed the CMake build")

if(TRDP_CONFIG)
    if(NOT COMMAND trdp_load_make_config)
        message(FATAL_ERROR "TrdpConfigLoader.cmake must be available to load legacy configs")
    endif()
    trdp_load_make_config("${TRDP_CONFIG}")
endif()

if(TRDP_CONFIG_LOADED)
    if(TRDP_CONFIG_SYSTEM_NAME_HINT AND NOT CMAKE_SYSTEM_NAME)
        set(CMAKE_SYSTEM_NAME "${TRDP_CONFIG_SYSTEM_NAME_HINT}")
    endif()
    if(TRDP_CONFIG_IS_CROSS)
        set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
    endif()
    if(TRDP_CONFIG_COMPILER AND NOT CMAKE_C_COMPILER)
        set(CMAKE_C_COMPILER "${TRDP_CONFIG_COMPILER}" CACHE FILEPATH "C compiler inferred from ${TRDP_CONFIG}" FORCE)
    endif()
    if(TRDP_CONFIG_AR AND NOT CMAKE_AR)
        set(CMAKE_AR "${TRDP_CONFIG_AR}" CACHE FILEPATH "Archiver inferred from ${TRDP_CONFIG}" FORCE)
    endif()
    if(TRDP_CONFIG_RANLIB AND NOT CMAKE_RANLIB)
        set(CMAKE_RANLIB "${TRDP_CONFIG_RANLIB}" CACHE FILEPATH "Ranlib inferred from ${TRDP_CONFIG}" FORCE)
    endif()
endif()

set(_trdp_target_os_default "LINUX")
if(DEFINED TRDP_CONFIG_TARGET_OS AND NOT TRDP_CONFIG_TARGET_OS STREQUAL "")
    set(_trdp_target_os_default "${TRDP_CONFIG_TARGET_OS}")
endif()

set(_trdp_vos_default "posix")
if(DEFINED TRDP_CONFIG_TARGET_VOS AND NOT TRDP_CONFIG_TARGET_VOS STREQUAL "")
    set(_trdp_vos_default "${TRDP_CONFIG_TARGET_VOS}")
endif()

project(TRDP VERSION 3.0.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(_trdp_md_default ON)
if(DEFINED TRDP_CONFIG_MD_SUPPORT AND NOT TRDP_CONFIG_MD_SUPPORT STREQUAL "")
    if(TRDP_CONFIG_MD_SUPPORT STREQUAL "0")
        set(_trdp_md_default OFF)
    else()
        set(_trdp_md_default ON)
    endif()
endif()

set(_trdp_tsn_default OFF)
if(DEFINED TRDP_CONFIG_TSN_SUPPORT AND NOT TRDP_CONFIG_TSN_SUPPORT STREQUAL "")
    if(TRDP_CONFIG_TSN_SUPPORT STREQUAL "0")
        set(_trdp_tsn_default OFF)
    else()
        set(_trdp_tsn_default ON)
    endif()
endif()

set(_trdp_soa_default OFF)
if(DEFINED TRDP_CONFIG_SOA_SUPPORT AND NOT TRDP_CONFIG_SOA_SUPPORT STREQUAL "")
    if(TRDP_CONFIG_SOA_SUPPORT STREQUAL "0")
        set(_trdp_soa_default OFF)
    else()
        set(_trdp_soa_default ON)
    endif()
endif()

set(_trdp_high_perf_default OFF)
if(DEFINED TRDP_CONFIG_HIGH_PERF_SUPPORT AND NOT TRDP_CONFIG_HIGH_PERF_SUPPORT STREQUAL "")
    if(TRDP_CONFIG_HIGH_PERF_SUPPORT STREQUAL "0")
        set(_trdp_high_perf_default OFF)
    else()
        set(_trdp_high_perf_default ON)
    endif()
endif()

set(_trdp_high_perf_base2_default OFF)
if(DEFINED TRDP_CONFIG_HIGH_PERF_BASE2 AND NOT TRDP_CONFIG_HIGH_PERF_BASE2 STREQUAL "")
    if(TRDP_CONFIG_HIGH_PERF_BASE2 STREQUAL "0")
        set(_trdp_high_perf_base2_default OFF)
    else()
        set(_trdp_high_perf_base2_default ON)
    endif()
elseif(_trdp_high_perf_default)
    set(_trdp_high_perf_base2_default ON)
endif()

set(_trdp_pd_unicast_default OFF)
if(DEFINED TRDP_CONFIG_PD_UNICAST_SUPPORT AND NOT TRDP_CONFIG_PD_UNICAST_SUPPORT STREQUAL "")
    if(TRDP_CONFIG_PD_UNICAST_SUPPORT STREQUAL "0")
        set(_trdp_pd_unicast_default OFF)
    else()
        set(_trdp_pd_unicast_default ON)
    endif()
endif()

set(_trdp_build_tsn_apps_default OFF)
if(_trdp_tsn_default)
    set(_trdp_build_tsn_apps_default ON)
endif()

option(TRDP_ENABLE_MD "Enable message data support" ${_trdp_md_default})
option(TRDP_ENABLE_XML "Enable XML parsing, marshalling and directory services" ON)
option(TRDP_ENABLE_TSN "Enable TSN socket support" ${_trdp_tsn_default})
option(TRDP_ENABLE_SOA "Enable service oriented architecture support" ${_trdp_soa_default})
option(TRDP_ENABLE_HIGH_PERF "Enable high performance indexed dataset support" ${_trdp_high_perf_default})
option(TRDP_ENABLE_HIGH_PERF_BASE2 "Use base 2 indexing for high performance datasets" ${_trdp_high_perf_base2_default})
option(TRDP_ENABLE_PD_UNICAST "Enable PD unicast support" ${_trdp_pd_unicast_default})

option(TRDP_BUILD_EXAMPLES "Build TRDP example applications" ON)
option(TRDP_BUILD_TEST_APPS "Build TRDP test utilities" ON)
option(TRDP_BUILD_XML_APPS "Build XML based utilities" ON)
option(TRDP_BUILD_VLAN_APPS "Build VLAN test utilities" ON)
option(TRDP_BUILD_MARSHALLING_APP "Build marshalling regression utility" ON)
option(TRDP_BUILD_TSN_APPS "Build TSN demo utilities" ${_trdp_build_tsn_apps_default})

if(TRDP_CONFIG_COMPILE_OPTIONS)
    add_compile_options(${TRDP_CONFIG_COMPILE_OPTIONS})
endif()

if(TRDP_CONFIG_COMPILE_DEFINITIONS)
    add_compile_definitions(${TRDP_CONFIG_COMPILE_DEFINITIONS})
endif()

if(TRDP_CONFIG_RT_THREADS AND NOT TRDP_CONFIG_RT_THREADS STREQUAL "" AND NOT TRDP_CONFIG_RT_THREADS STREQUAL "0")
    add_compile_definitions(RT_THREADS)
endif()

set(TRDP_TARGET_OS "${_trdp_target_os_default}" CACHE STRING "Value passed via -D<OS> compile definition")
set(TRDP_VOS_IMPLEMENTATION "${_trdp_vos_default}" CACHE STRING "Name of the VOS implementation directory")
set_property(CACHE TRDP_VOS_IMPLEMENTATION PROPERTY STRINGS posix)

set(_trdp_output_arch "${TRDP_CONFIG_ARCH}")
if(NOT _trdp_output_arch OR _trdp_output_arch STREQUAL "unknown")
    if(CMAKE_SYSTEM_PROCESSOR)
        string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" _trdp_output_arch)
    else()
        set(_trdp_output_arch "unknown")
    endif()
endif()

set(_trdp_output_root "${CMAKE_SOURCE_DIR}/bld/output/${_trdp_output_arch}")

if(CMAKE_CONFIGURATION_TYPES)
    foreach(_cfg ${CMAKE_CONFIGURATION_TYPES})
        string(TOLOWER "${_cfg}" _trdp_cfg_lower)
        if(_trdp_cfg_lower STREQUAL "debug")
            set(_trdp_suffix "dbg")
        else()
            set(_trdp_suffix "rel")
        endif()
        set(_trdp_cfg_dir "${_trdp_output_root}-${_trdp_suffix}")
        set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${_cfg} "${_trdp_cfg_dir}")
        set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${_cfg} "${_trdp_cfg_dir}")
        set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${_cfg} "${_trdp_cfg_dir}")
    endforeach()
else()
    string(TOLOWER "${CMAKE_BUILD_TYPE}" _trdp_build_type)
    if(_trdp_build_type STREQUAL "debug")
        set(_trdp_suffix "dbg")
    else()
        set(_trdp_suffix "rel")
    endif()
    set(_trdp_cfg_dir "${_trdp_output_root}-${_trdp_suffix}")
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${_trdp_cfg_dir}")
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${_trdp_cfg_dir}")
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${_trdp_cfg_dir}")
endif()

set(TRDP_COMMON_SOURCES
    src/common/trdp_pdcom.c
    src/common/trdp_utils.c
    src/common/tlp_if.c
    src/common/tlc_if.c
    src/common/trdp_stats.c
    src/common/tau_so_if.c
)

set(TRDP_VOS_COMMON_SOURCES
    src/vos/common/vos_mem.c
    src/vos/common/vos_utils.c
)

set(TRDP_VOS_IMPL_SOURCES
    src/vos/${TRDP_VOS_IMPLEMENTATION}/vos_sock.c
    src/vos/${TRDP_VOS_IMPLEMENTATION}/vos_thread.c
    src/vos/${TRDP_VOS_IMPLEMENTATION}/vos_shared_mem.c
)

if(TRDP_ENABLE_MD)
    list(APPEND TRDP_COMMON_SOURCES
        src/common/trdp_mdcom.c
        src/common/tlm_if.c
    )
endif()

if(TRDP_ENABLE_XML)
    list(APPEND TRDP_COMMON_SOURCES
        src/common/trdp_xml.c
        src/common/tau_xml.c
        src/common/tau_marshall.c
        src/common/tau_dnr.c
        src/common/tau_tti.c
        src/common/tau_ctrl.c
        src/common/tau_cstinfo.c
    )
endif()

if(TRDP_ENABLE_HIGH_PERF)
    list(APPEND TRDP_COMMON_SOURCES src/common/trdp_pdindex.c)
endif()

if(TRDP_ENABLE_TSN)
    list(APPEND TRDP_VOS_IMPL_SOURCES src/vos/${TRDP_VOS_IMPLEMENTATION}/vos_sockTSN.c)
endif()

add_library(trdp STATIC
    ${TRDP_COMMON_SOURCES}
    ${TRDP_VOS_COMMON_SOURCES}
    ${TRDP_VOS_IMPL_SOURCES}
)

add_library(trdp::trdp ALIAS trdp)

target_include_directories(trdp
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/api>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/common>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/vos/api>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/vos/common>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/vos/${TRDP_VOS_IMPLEMENTATION}>
        ${TRDP_CONFIG_INCLUDE_DIRS}
)

if(TRDP_CONFIG_LINK_DIRECTORIES)
    target_link_directories(trdp PUBLIC ${TRDP_CONFIG_LINK_DIRECTORIES})
endif()

if(TRDP_CONFIG_LINK_OPTIONS)
    target_link_options(trdp PUBLIC ${TRDP_CONFIG_LINK_OPTIONS})
endif()

if(TRDP_CONFIG_LINK_LIBRARIES)
    target_link_libraries(trdp PUBLIC ${TRDP_CONFIG_LINK_LIBRARIES})
endif()

find_package(Threads REQUIRED)
target_link_libraries(trdp PUBLIC Threads::Threads)

find_library(RT_LIBRARY rt)
if(RT_LIBRARY)
    target_link_libraries(trdp PUBLIC ${RT_LIBRARY})
endif()

set(_uuid_required FALSE)
set(_uuid_definition_index -1)
if(TRDP_CONFIG_COMPILE_DEFINITIONS)
    list(FIND TRDP_CONFIG_COMPILE_DEFINITIONS "HAS_UUID" _uuid_definition_index)
    if(NOT _uuid_definition_index EQUAL -1)
        set(_uuid_required TRUE)
    endif()
endif()

if(NOT DEFINED TRDP_CONFIG_LOADED OR NOT TRDP_CONFIG_LOADED)
    set(_uuid_required TRUE)
endif()

if(_uuid_required)
    set(_uuid_header_found FALSE)
    set(_uuid_include_dir "")

    if(TRDP_CONFIG_INCLUDE_DIRS)
        foreach(_inc IN LISTS TRDP_CONFIG_INCLUDE_DIRS)
            if(EXISTS "${_inc}/uuid/uuid.h")
                set(_uuid_header_found TRUE)
                set(_uuid_include_dir "${_inc}")
                break()
            elseif(EXISTS "${_inc}/uuid.h")
                set(_uuid_header_found TRUE)
                set(_uuid_include_dir "${_inc}")
                break()
            endif()
        endforeach()
    endif()

    if(NOT _uuid_header_found AND (NOT TRDP_CONFIG_LOADED OR NOT TRDP_CONFIG_IS_CROSS))
        find_path(UUID_INCLUDE_DIR NAMES uuid/uuid.h)
        if(UUID_INCLUDE_DIR)
            set(_uuid_header_found TRUE)
            set(_uuid_include_dir "${UUID_INCLUDE_DIR}")
        endif()
    endif()

    if(NOT _uuid_header_found)
        if(TRDP_CONFIG)
            message(
                FATAL_ERROR
                "TRDP config '${TRDP_CONFIG}' enables HAS_UUID but 'uuid/uuid.h' was not found. "
                "Install the uuid development headers or extend INCPATH to point to the "
                "correct sysroot before configuring CMake."
            )
        else()
            message(FATAL_ERROR "uuid/uuid.h could not be located; install the uuid development headers.")
        endif()
    endif()

    if(NOT _uuid_include_dir STREQUAL "")
        set(_needs_uuid_include TRUE)
        if(TRDP_CONFIG_INCLUDE_DIRS)
            list(FIND TRDP_CONFIG_INCLUDE_DIRS "${_uuid_include_dir}" _uuid_include_index)
            if(NOT _uuid_include_index EQUAL -1)
                set(_needs_uuid_include FALSE)
            endif()
        endif()
        if(_needs_uuid_include)
            target_include_directories(trdp PUBLIC ${_uuid_include_dir})
        endif()
    endif()

    set(_uuid_library_provided FALSE)
    if(TRDP_CONFIG_LINK_LIBRARIES)
        list(FIND TRDP_CONFIG_LINK_LIBRARIES "uuid" _uuid_library_index)
        if(NOT _uuid_library_index EQUAL -1)
            set(_uuid_library_provided TRUE)
        endif()
    endif()

    if(NOT _uuid_library_provided)
        find_library(UUID_LIBRARY NAMES uuid)
        if(NOT UUID_LIBRARY)
            if(TRDP_CONFIG)
                message(
                    FATAL_ERROR
                    "TRDP config '${TRDP_CONFIG}' enables HAS_UUID but libuuid could not be located. "
                    "Install the uuid development package or extend LDFLAGS/ADD_LIBPATH with the "
                    "correct sysroot library directory."
                )
            else()
                message(FATAL_ERROR "libuuid could not be located; install the uuid development package.")
            endif()
        endif()
        target_link_libraries(trdp PUBLIC ${UUID_LIBRARY})
    endif()

    if(_uuid_definition_index EQUAL -1)
        target_compile_definitions(trdp PUBLIC HAS_UUID)
    endif()
endif()

set(_trdp_public_compile_definitions ${TRDP_TARGET_OS})

if(TRDP_CONFIG_COMPILE_DEFINITIONS)
    foreach(_def IN LISTS TRDP_CONFIG_COMPILE_DEFINITIONS)
        list(FIND _trdp_public_compile_definitions "${_def}" _def_index)
        if(_def_index EQUAL -1)
            list(APPEND _trdp_public_compile_definitions "${_def}")
        endif()
    endforeach()
endif()

foreach(_fallback_def POSIX _GNU_SOURCE L_ENDIAN)
    list(FIND _trdp_public_compile_definitions "${_fallback_def}" _fallback_index)
    if(_fallback_index EQUAL -1)
        list(APPEND _trdp_public_compile_definitions "${_fallback_def}")
    endif()
endforeach()

list(REMOVE_ITEM _trdp_public_compile_definitions "")

target_compile_definitions(trdp PUBLIC ${_trdp_public_compile_definitions})

if(TRDP_ENABLE_MD)
    target_compile_definitions(trdp PUBLIC MD_SUPPORT=1)
else()
    target_compile_definitions(trdp PUBLIC MD_SUPPORT=0)
endif()

if(TRDP_ENABLE_TSN)
    target_compile_definitions(trdp PUBLIC TSN_SUPPORT=1)
endif()

if(TRDP_ENABLE_SOA)
    target_compile_definitions(trdp PUBLIC SOA_SUPPORT=1)
endif()

if(TRDP_ENABLE_PD_UNICAST)
    target_compile_definitions(trdp PUBLIC PD_UNICAST_SUPPORT=1)
endif()

if(TRDP_ENABLE_HIGH_PERF)
    target_compile_definitions(trdp PUBLIC HIGH_PERF_INDEXED)
    if(TRDP_ENABLE_HIGH_PERF_BASE2)
        target_compile_definitions(trdp PUBLIC HIGH_PERF_BASE2)
    endif()
endif()

target_compile_options(trdp
    PRIVATE
        -Wall
        -fstrength-reduce
        -fno-builtin
        -fsigned-char
        -Wno-unknown-pragmas
        -Wno-format
        -Wno-unused-label
        -Wno-unused-function
        -Wno-int-to-void-pointer-cast
        -Wno-self-assign
)

function(trdp_add_program target)
    add_executable(${target} ${ARGN})
    target_link_libraries(${target} PRIVATE trdp::trdp)
endfunction()

if(TRDP_BUILD_EXAMPLES)
    trdp_add_program(echoCallback example/echoCallback.c)
    trdp_add_program(receivePolling example/echoPolling.c)
    trdp_add_program(sendHello example/sendHello.c)
    trdp_add_program(receiveHello example/receiveHello.c)
    trdp_add_program(sendData example/sendData.c)
    trdp_add_program(sourceFiltering example/sourceFilter/sourceFiltering.c)

    if(TRDP_BUILD_TSN_APPS AND TRDP_ENABLE_TSN)
        trdp_add_program(sendTSN example/TSN/sendTSN.c)
        trdp_add_program(receiveTSN example/TSN/receiveTSN.c)
    endif()
endif()

if(TRDP_BUILD_TEST_APPS)
    trdp_add_program(getStats test/diverse/getStats.c)
    trdp_add_program(vostest test/diverse/LibraryTests.c)
    trdp_add_program(MCreceiver test/diverse/MCreceiver.c)
    trdp_add_program(test_mdSingle test/diverse/test_mdSingle.c)
    trdp_add_program(inaugTest test/diverse/inaugTest.c)
    trdp_add_program(pdPull test/diverse/pdPull.c)
    trdp_add_program(localtest test/localtest/api_test.c)
    trdp_add_program(localtest2 test/localtest/api_test_2.c)
    trdp_add_program(localtest3 test/localtest/api_test_3.c)
    trdp_add_program(localtest4 test/localtest/api_test_4.c)
    trdp_add_program(pdMcRouting test/diverse/pdMcRoutingTest.c)
    trdp_add_program(mdDataLength test/diverse/mdDataLengthTest.c)
    trdp_add_program(trdp_pd_test test/pdpatterns/trdp-pd-test.c)
    set_target_properties(trdp_pd_test PROPERTIES OUTPUT_NAME trdp-pd-test)
    trdp_add_program(pd_responder test/diverse/pd_responder.c)
    trdp_add_program(testSub test/diverse/subTest.c)
    trdp_add_program(trdp_md_test test/mdpatterns/trdp-md-test.c)
    set_target_properties(trdp_md_test PROPERTIES OUTPUT_NAME trdp-md-test)
    trdp_add_program(trdp_md_test_fast test/mdpatterns/trdp-md-test-fast.c)
    set_target_properties(trdp_md_test_fast PROPERTIES OUTPUT_NAME trdp-md-test-fast)
    trdp_add_program(trdp_md_reptestcaller test/mdpatterns/rep-testcaller.c)
    set_target_properties(trdp_md_reptestcaller PROPERTIES OUTPUT_NAME trdp-md-reptestcaller)
    trdp_add_program(trdp_md_reptestreplier test/mdpatterns/rep-testreplier.c)
    set_target_properties(trdp_md_reptestreplier PROPERTIES OUTPUT_NAME trdp-md-reptestreplier)

    foreach(local_loop_target IN ITEMS localtest localtest2 localtest3 localtest4 test_mdSingle)
        target_compile_options(${local_loop_target} PRIVATE -Wno-unused-variable)
    endforeach()
endif()

if(TRDP_BUILD_XML_APPS)
    trdp_add_program(trdp_xmlprint_test test/xml/trdp-xmlprint-test.c)
    set_target_properties(trdp_xmlprint_test PROPERTIES OUTPUT_NAME trdp-xmlprint-test)
    trdp_add_program(trdp_xmlpd_test test/xml/trdp-xmlpd-test.c)
    set_target_properties(trdp_xmlpd_test PROPERTIES OUTPUT_NAME trdp-xmlpd-test)
endif()

if(TRDP_BUILD_VLAN_APPS)
    trdp_add_program(trdp_md_test_vlan test/mdpatterns/trdp-md-test-vlan.c)
    set_target_properties(trdp_md_test_vlan PROPERTIES OUTPUT_NAME trdp-md-test-vlan)
    trdp_add_program(trdp_pd_test_vlan test/pdpatterns/trdp-pd-test-vlan.c)
    set_target_properties(trdp_pd_test_vlan PROPERTIES OUTPUT_NAME trdp-pd-test-vlan)
endif()

if(TRDP_BUILD_MARSHALLING_APP)
    trdp_add_program(test_marshalling test/marshalling/test_marshalling.c)
endif()

if(TRDP_BUILD_TEST_APPS)
    # The PD responder subscribes to PD publishers and expects definitions from optional modules
    add_dependencies(pd_responder trdp_md_test trdp_pd_test)
endif()

