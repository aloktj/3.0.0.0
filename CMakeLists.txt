cmake_minimum_required(VERSION 3.16)
project(TRDP VERSION 3.0.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(TRDP_ENABLE_MD "Enable message data support" ON)
option(TRDP_ENABLE_XML "Enable XML parsing, marshalling and directory services" ON)
option(TRDP_ENABLE_TSN "Enable TSN socket support" OFF)
option(TRDP_ENABLE_SOA "Enable service oriented architecture support" OFF)
option(TRDP_ENABLE_HIGH_PERF "Enable high performance indexed dataset support" OFF)
option(TRDP_ENABLE_PD_UNICAST "Enable PD unicast support" OFF)

option(TRDP_BUILD_EXAMPLES "Build TRDP example applications" ON)
option(TRDP_BUILD_TEST_APPS "Build TRDP test utilities" ON)
option(TRDP_BUILD_XML_APPS "Build XML based utilities" ON)
option(TRDP_BUILD_VLAN_APPS "Build VLAN test utilities" ON)
option(TRDP_BUILD_MARSHALLING_APP "Build marshalling regression utility" ON)
option(TRDP_BUILD_TSN_APPS "Build TSN demo utilities" OFF)

set(TRDP_TARGET_OS "LINUX" CACHE STRING "Value passed via -D<OS> compile definition")
set(TRDP_VOS_IMPLEMENTATION "posix" CACHE STRING "Name of the VOS implementation directory")
set_property(CACHE TRDP_VOS_IMPLEMENTATION PROPERTY STRINGS posix)

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
)

find_package(Threads REQUIRED)
target_link_libraries(trdp PUBLIC Threads::Threads)

find_library(RT_LIBRARY rt)
if(RT_LIBRARY)
    target_link_libraries(trdp PUBLIC ${RT_LIBRARY})
endif()

find_library(UUID_LIBRARY uuid)
if(UUID_LIBRARY)
    target_link_libraries(trdp PUBLIC ${UUID_LIBRARY})
    target_compile_definitions(trdp PUBLIC HAS_UUID)
endif()

target_compile_definitions(trdp
    PUBLIC
        ${TRDP_TARGET_OS}
        POSIX
        _GNU_SOURCE
        L_ENDIAN
)

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
    target_compile_definitions(trdp PUBLIC HIGH_PERF_INDEXED HIGH_PERF_BASE2)
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

