#!/bin/zsh

source ~/.local/lib/distcc-driver/distcc.sh

main() {
	# mkdir -p /home/gamesh411/clang-rwa/
	cd /home/gamesh411/clang-rwa
        # cmake ../llvm-project/llvm --preset release
        # distcc_build cmake --build . -- clang
        cmake --build . -- clang
}

main "$@"
