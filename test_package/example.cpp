#include <liblava/lava.hpp>
#include <filesystem>
#include <iostream>

int main(int argc, char** argv) {
    std::cout << std::filesystem::current_path() << std::endl;
    return lava::check(VK_SUCCESS) ? 0 : 1;
}
