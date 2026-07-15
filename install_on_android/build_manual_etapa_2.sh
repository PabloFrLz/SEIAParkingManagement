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

echo ">>> ETAPA 2: apk (empacotando o APK final)"
python3.11 -m pythonforandroid.toolchain apk \
  --bootstrap qt \
  --dist_name SEIAParkingManagement \
  --name "SEIA Parking Management" \
  --version 0.1 \
  --package org.seiaparkingmanagement.seiaparkingmanagement \
  --minsdk 21 \
  --ndk-api 21 \
  --private "$PROJECT_DIR/.buildozer/android/app" \
  --permission android.permission.WRITE_EXTERNAL_STORAGE \
  --permission android.permission.INTERNET \
  --android-entrypoint org.kivy.android.PythonActivity \
  --android-apptheme @android:style/Theme.NoTitleBar \
  --add-jar "$JARS_DIR/Qt6AndroidBindings.jar" \
  --add-jar "$JARS_DIR/Qt6Android.jar" \
  --icon "$ICON" \
  --orientation portrait \
  --window \
  --enable-androidx \
  --copy-libs \
  --local-recipes="$RECIPE_DIR" \
  --arch arm64-v8a \
  --storage-dir="$STORAGE_DIR" \
  --ndk-api=21 \
  --ignore-setup-py \
  --debug \
  --qt-libs=Gui,Widgets,Core \
  --load-local-libs=plugins_platforms_qtforandroid

echo ">>> Concluído! Verificando se libpython3.11.so está no APK..."
find "$PROJECT_DIR" -maxdepth 1 -name "*.apk" -exec unzip -l {} \; | grep -i libpython