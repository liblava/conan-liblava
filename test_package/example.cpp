#include <filesystem>
#include <iostream>
#include <liblava/lava.hpp>

int main(int argc, char **argv) {
  std::cout << std::filesystem::current_path() << std::endl;
  lava::engine app("example", {argc, argv});
  if (!app.setup())
    return lava::error::not_ready;
  return 0;
}
