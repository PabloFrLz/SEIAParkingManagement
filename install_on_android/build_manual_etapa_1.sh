#!/bin/bash
set -e

# Ative a venv antes de rodar este script:
# source ~/pyside-android-venv/bin/activate

PROJECT_DIR=~/SEIAParkingManagement
SDK_PATH=~/.pyside6_android_deploy/android-sdk
NDK_PATH=~/.pyside6_android_deploy/android-sdk/ndk/26.1.10909125
RECIPE_DIR=$PROJECT_DIR/deployment/recipes
JARS_DIR=$PROJECT_DIR/deployment/jar/PySide6/jar
STORAGE_DIR=$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a
ICON=~/pyside-android-venv/lib/python3.11/site-packages/PySide6/scripts/deploy_lib/pyside_icon.jpg

export ANDROIDSDK=$SDK_PATH
export ANDROIDNDK=$NDK_PATH
export ANDROIDAPI=31
export ANDROIDMINAPI=21

cd "$PROJECT_DIR"

echo ">>> ETAPA 1: create (compilando Python 3.11 fixo + todas as libs)"
python3.11 -m pythonforandroid.toolchain create \
  --dist_name=SEIAParkingManagement \
  --bootstrap=qt \
  --requirements=python3==3.11.9,hostpython3==3.11.9,shiboken6,PySide6,pymysql,pyqtdarktheme,colorama,pypdf,requests,Pillow \
  --arch=arm64-v8a \
  --copy-libs \
  --local-recipes="$RECIPE_DIR" \
  --storage-dir="$STORAGE_DIR" \
  --ndk-api=21 \
  --ignore-setup-py \
  --debug \
  --qt-libs=Gui,Widgets,Core \
  --load-local-libs=plugins_platforms_qtforandroid