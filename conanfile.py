import os
import shutil
from conans import ConanFile, CMake, tools

class LiblavaConan(ConanFile):
    name = "liblava"
    version = "0.7.3"
    license = "MIT"
    author = "Lava Block OÜ (code@liblava.dev)"
    url = "https://liblava.dev"
    description = "A modern and easy-to-use library for the Vulkan API"
    topics = ("vulkan", "graphics", "rendering")
    settings = "os", "compiler", "build_type", "arch"
    # TODO shared library build
    # requires changes to liblava CMakeLists.txt and settings for subrepos
    options = {
        "fPIC": [True, False],
        "test": [True, False],
        "demo": [True, False],
        #"shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "test": False,
        "demo": False,
        #"shared": False
    }
    generators = "cmake"
    no_copy_source=True

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON" if self.options.get_safe("fPIC") else "OFF"
        cmake.definitions["LIBLAVA_TEST"] = "ON" if self.options.get_safe("test") else "OFF"
        cmake.definitions["LIBLAVA_DEMO"] = "ON" if self.options.get_safe("demo") else "OFF"
        cmake.definitions["LIBLAVA_TEMPLATE"] = "OFF"
        cmake.configure()
        return cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        # Check if the current profile config supports C++20
        tools.check_min_cppstd(self, "20")

    def source(self):
        git = tools.Git()
        git.clone(self.url)
        git.checkout(self.version)

        # guarantee proper /MT /MD linkage in MSVC
        project_line = "project(liblava VERSION {} LANGUAGES C CXX)".format(self.version)
        tools.replace_in_file("CMakeLists.txt", project_line,
                              '''
                              {}
                              include(${{CMAKE_BINARY_DIR}}/conanbuildinfo.cmake)
                              conan_basic_setup()
                              '''
                              .format(project_line))

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        shutil.rmtree(os.path.join(self.package_folder, "lib/cmake"), ignore_errors=True)
        self.copy("LICENSE", dst="licenses", src=self.source_folder)

    def package_info(self):
        self.cpp_info.includedirs = [
            "include",
            "include/liblava/ext"
        ]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]

        self.cpp_info.cxxflags += [tools.cppstd_flag(self.settings)]
        self.cpp_info.defines += ["SPDLOG_COMPILED_LIB"]

        self.cpp_info.libs = [
            # in correct linking order
            "lava.engine",
            "lava.app",
            "lava.block",
            "lava.frame",
            "lava.asset",
            "lava.resource",
            "lava.base",
            "lava.file",
            "lava.util",
            "lava.core",
            "shaderc_combined",
            "glfw3",
            "physfs" if self.settings.compiler != "Visual Studio" else "physfs-static",
            "spdlog"
        ]

        # std::filesystem library
        if self.settings.get_safe("compiler.libcxx") == "libstdc++11":
            self.cpp_info.system_libs += ["stdc++fs"]

        if self.settings.get_safe("compiler") in ["gcc", "clang"]:
            thread_flag = "-pthread"
            self.cpp_info.cxxflags        += [thread_flag]
            self.cpp_info.sharedlinkflags += [thread_flag]
            self.cpp_info.exelinkflags    += [thread_flag]
            self.cpp_info.system_libs += ["dl"]
