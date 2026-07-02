[app]
title = Calculadora Uber
package.name = calculadora_uber
package.domain = org.allface
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,csv
version = 1.0
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Permissões do Android
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
