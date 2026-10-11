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
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

p4a.fork = kivy
p4a.branch = v2024.01.21
p4a.local_recipes = ./p4a_recipes

[buildozer]
log_level = 2
warn_on_root = 0
