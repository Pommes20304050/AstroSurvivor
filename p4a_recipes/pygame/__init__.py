from pythonforandroid.recipes.pygame import PygameRecipe as _OriginalPygameRecipe


class PygameRecipe(_OriginalPygameRecipe):
    version = '2.6.1'
    url = 'https://github.com/pygame/pygame/archive/refs/tags/{version}.tar.gz'
    patches = []


recipe = PygameRecipe()
