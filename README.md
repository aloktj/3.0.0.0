# TRDP 3.0.0.0

This repository contains the 3.0.0.0 release of the TRDP stack together with the
reference command line tools.  The original build system is based on GNU Make
configuration files and remains available.  A portable CMake build description
was added so that the stack can be consumed as a sub-project (for example from
the TRDPSimulator application) without maintaining a parallel build system.

## Building with the Make based toolchain

1. Pick the configuration that matches your platform, e.g. `make POSIX_X86_config`
   or `make LINUX_X86_64_config`.  The selected configuration is copied to
   `config/config.mk`.
2. Invoke `make` (optionally with `DEBUG=TRUE`, `MD_SUPPORT=0`, …).  The build
   artefacts are generated in `bld/output/<arch>-<variant>` and mirror the
   layout that is documented in `readme-makefile.txt`.

Use `make clean` to remove the previously generated binaries.  All commands from
`make help` continue to work exactly as before.

## Building with CMake

```
cmake -S . -B build -DTRDP_BUILD_EXAMPLES=ON -DTRDP_BUILD_TEST_APPS=ON
cmake --build build
```

To mirror one of the legacy GNU Make configurations, including cross-compiling
compiler prefixes and the associated feature toggles, set `TRDP_CONFIG` to the
file name from the `config/` directory before configuring CMake. For example:

```
cmake -S . -B build -DTRDP_CONFIG=LINUX_sama5d27_config
cmake --build build
```

The loader applies the toolchain path/prefix/postfix from the selected file,
seeds the default option values (MD, TSN, SOA, high-performance indexing,
PD unicast, etc.) and maps the build outputs into the same
`bld/output/<arch>-<variant>` layout that the Makefiles use.

To check a CMake configuration against every legacy preset, run
`scripts/verify_cmake_configs.py`.  The helper walks through `config/` and
invokes CMake for each file, mirroring the manual verification process.  When
cross toolchains are not present locally (for example the VxWorks or Yocto
SDKs referenced by the makefiles) the script surfaces the missing compiler or
environment variables in its summary so the required vendor packages can be
installed before attempting a full build.  If you pass `--generator`, ensure
that the corresponding build tool is installed; otherwise omit the option and
let CMake fall back to its default generator.

The default configuration mirrors the Linux make configuration: it enables
message data support and the optional XML/directory modules, links against
`pthread`, `rt` and `uuid`, and builds the example as well as test utilities.
CMake options expose the switches that were previously provided through make
variables:

- `TRDP_ENABLE_MD`, `TRDP_ENABLE_XML`, `TRDP_ENABLE_TSN`, `TRDP_ENABLE_SOA`,
  `TRDP_ENABLE_HIGH_PERF`, `TRDP_ENABLE_HIGH_PERF_BASE2`, `TRDP_ENABLE_PD_UNICAST`
- `TRDP_BUILD_EXAMPLES`, `TRDP_BUILD_TEST_APPS`, `TRDP_BUILD_XML_APPS`,
  `TRDP_BUILD_VLAN_APPS`, `TRDP_BUILD_MARSHALLING_APP`, `TRDP_BUILD_TSN_APPS`
- `TRDP_TARGET_OS` (defaults to `LINUX`) and `TRDP_VOS_IMPLEMENTATION`
  (defaults to `posix`)

The resulting static library is provided as the `trdp::trdp` target and the
executables keep their historic names.  Projects that include the stack as a
subdirectory only need to link against `trdp::trdp` and may selectively enable
additional tools and features via the options listed above.
