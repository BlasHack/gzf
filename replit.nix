{pkgs}: {
  deps = [
    pkgs.libopus
    pkgs.ffmpeg-full
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libopus
    ];
  };
}
