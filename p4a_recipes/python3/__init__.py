from pythonforandroid.recipes.python3 import Python3Recipe as BasePython3Recipe


class Python3Recipe(BasePython3Recipe):
    """
    Local override: relax Android NDK bionic libc incompatibilities.
    NDK sysroot is missing some POSIX functions (setgrent/getgrent/endgrent)
    which trip -Werror=implicit-function-declaration under clang 14+.
    Downgrade that specific error to a warning so python3 can finish building.
    """

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch=arch, with_flags_in_cc=with_flags_in_cc)
        extra = ' -Wno-error=implicit-function-declaration'
        env['CFLAGS'] = env.get('CFLAGS', '') + extra
        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + extra
        return env


recipe = Python3Recipe()
