@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =========================
:: Finalizador Anti-Engasgos (v5)
:: =========================
:: - Corrige parsing do ffprobe (usa arquivo temporario)
:: - Executa em ordem com verificacao de existencia apos cada etapa
:: - Substitui -vsync cfr por -fps_mode cfr (FFmpeg 7)
:: - keyint ~= 2s (fps*2) automaticamente

set "SRC_DIR=D:\PROJETOS PYTHON 2025\BMA_VF\BelarminoMonteiroAdvogado\static\videos"
set "TARGETS=maior-1.mp4 maior-1.webm"

where ffmpeg >nul 2>&1 || (
  echo [ERRO] FFmpeg nao encontrado no PATH.
  goto :end
)
where ffprobe >nul 2>&1 || (
  echo [ERRO] FFprobe nao encontrado no PATH.
  goto :end
)

for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"') do set DATESTAMP=%%I
set "OUT=%SRC_DIR%\renders_final_%DATESTAMP%"
if not exist "%OUT%" mkdir "%OUT%"
set "LOG=%OUT%\finalizer_%DATESTAMP%.log"

echo ===== Finalizador Anti-Engasgos v5 ===== > "%LOG%"
echo SRC_DIR=%SRC_DIR% >> "%LOG%"
echo OUT_DIR=%OUT% >> "%LOG%"

echo.
echo ===== Iniciando =====

for %%F in (%TARGETS%) do (
  set "INFILE=%SRC_DIR%\%%~F"
  set "BASE=%%~nF"
  set "REMUXMKV=%OUT%\%%~nF_remux_genpts.mkv"
  set "REPACKMP4=%OUT%\%%~nF_fixado.mp4"
  set "TMPFPS=%OUT%\%%~nF_fps.txt"

  if not exist "!INFILE!" (
    echo [AVISO] Nao encontrado: "!INFILE!"
    (echo [WARN] Nao encontrado: "!INFILE!")>> "%LOG%"
  ) else (
    echo --- Arquivo: %%~F ---
    (echo --- Arquivo: %%~F ---)>> "%LOG%"

    rem 0) Detectar FPS original via ffprobe (avg_frame_rate) -> arquivo
    ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 "!INFILE!" > "!TMPFPS!" 2>> "%LOG%"
    set "FPS_ORIG="
    for /f "usebackq tokens=*" %%R in ("!TMPFPS!") do set "FPS_ORIG=%%R"
    if not defined FPS_ORIG set "FPS_ORIG=30"

    rem 0.1) keyint ~= 2s
    for /f %%K in ('powershell -NoProfile -Command "param([string]$r); $n,$d=$r.Split('/'); if($d){$fps=[double]$n/[double]$d}else{$fps=[double]$r}; $kf=[math]::Max([int][math]::Round($fps*2),1); Write-Output $kf" !FPS_ORIG!') do set "KEYINT=%%K"
    if not defined KEYINT set "KEYINT=60"
    echo [INFO] avg_frame_rate: !FPS_ORIG! ^| KEYINT: !KEYINT! >> "%LOG%"

    rem 1) Remux MKV com genpts
    echo [RUN] remux genpts: "!INFILE!" >> "%LOG%"
    ffmpeg -hide_banner -y -fflags +genpts -i "!INFILE!" -map 0 -c copy -avoid_negative_ts make_zero "!REMUXMKV!" >> "%LOG%" 2>&1
    if not exist "!REMUXMKV!" (
      echo [ERRO] Falhou remux: "!REMUXMKV!" nao foi criado. >> "%LOG%"
      echo [ERRO] Falhou remux: "!REMUXMKV!" nao foi criado.
      goto continue_loop
    )

    rem 2) Repack MP4 com timescale=1000 e faststart (+ max_interleave_delta 0)
    echo [RUN] repack mp4: "!REMUXMKV!" >> "%LOG%"
    ffmpeg -hide_banner -y -i "!REMUXMKV!" -map 0 -c copy -movflags +faststart -video_track_timescale 1000 -max_interleave_delta 0 "!REPACKMP4!" >> "%LOG%" 2>&1
    if not exist "!REPACKMP4!" (
      echo [ERRO] Falhou repack: "!REPACKMP4!" nao foi criado. >> "%LOG%"
      echo [ERRO] Falhou repack: "!REPACKMP4!" nao foi criado.
      goto continue_loop
    )

    rem 3) Reencode H.264 CFR no FPS original (sem audio)
    echo [RUN] h264 CFR @!FPS_ORIG! (keyint !KEYINT!) >> "%LOG%"
    ffmpeg -hide_banner -y -fflags +genpts -i "!REPACKMP4!" -map 0:v -an -sn -fps_mode cfr ^
      -vf "fps=!FPS_ORIG!" -c:v libx264 -preset veryslow -crf 14 -pix_fmt yuv420p ^
      -x264-params "keyint=!KEYINT!:min-keyint=!KEYINT!:scenecut=0" -movflags +faststart "!OUT!\!BASE!_h264_cfr_!FPS_ORIG!fps.mp4" >> "%LOG%" 2>&1

  )
  :continue_loop
)

echo.
echo ===== Concluido =====
echo Saidas em: "%OUT%"
echo Log: "%LOG%"
(echo ===== Concluido =====)>> "%LOG%"
pause

:end
