{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.ffmpeg-full
    pkgs.openssl
    pkgs.postgresql
  ];
}
