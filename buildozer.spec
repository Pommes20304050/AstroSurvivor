[app]
title = AstroSurvivor
package.name = astrosurvivor
package.domain = com.pommes

source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf,json,ico
source.include_patterns = assets/*,assets/**/*,locales/*,locales/**/*
source.exclude_dirs = build,bin,.buildozer,build-cache,web-cache,__pycache__
source.exclude_patterns = *.apk,*.aab,*.zip,*.tar.gz,*.exe,*.bat,save.json

version = 0.2
requirements = python3,pygame

orientation = landscape
fullscreen = 1

android.permissions = INTERNET
android.api = 33
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

p4a.source_dir = ./python-for-android
p4a.local_recipes = ./p4a_recipes

[buildozer]
log_level = 2
warn_on_root = 0
