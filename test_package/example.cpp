#include <liblava/lava.hpp>
#include <filesystem>
#include <iostream>

int main(int argc, char** argv)
{
    std::cout << std::filesystem::current_path() << std::endl;
    lava::app app("example", { argc, argv });
    if(!app.setup())
        return lava::error::not_ready;
    return 0;
}
