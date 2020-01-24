from distutils.core import setup
from Cython.Build import cythonize

# all .pyx files in a folder
setup(
    name='height_map',
    ext_modules=cythonize(["*.pyx"],
    compiler_directives={'language_level': "3"}),
)
