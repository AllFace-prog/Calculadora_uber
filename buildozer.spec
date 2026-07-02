[app]

# (str) Title of your application
title = Meu Aplicativo Kivy

# (str) Package name
package.name = meu_app

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# =============================================================================
# A LINHA IMPORTANTE CORRIGIDA ESTÁ LOGO ABAIXO:
# =============================================================================
requirements = python3, kivy==master, cython==0.29.36

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# =============================================================================
# Configurações do Android
# =============================================================================

# (list) Permissions
# android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) Architecture to build for (arm64-v8a e armeabi-v7a cobrem quase todos os celulares)
android.archs = arm64-v8a, armeabi-v7a

# (bool) skips dist cleanup to speed up compilation
android.skip_cleanup = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

