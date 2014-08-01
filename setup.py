import os
import glob

with_setuptools = False
if 'USE_SETUPTOOLS' in os.environ or 'pip' in __file__:
  try:
    from setuptools.command.install import install
    from setuptools import setup
    from setuptools import Extension
    from setuptools.command.build_ext import build_ext
    with_setuptools = True
  except:
    with_setuptools = False

if with_setuptools is False:
 from distutils.command.install import install
 from distutils.core import setup
 from distutils.core import Extension
 from distutils.command.build_ext import build_ext

# sorry for this, welcome feedback on the "right" way.
# shipping pre-compiled bainries on windows, have
# to hack things up here.

class mybuild(build_ext):
    def run(self):
        if "nt" in os.name:
            print "On Windows, skipping build_ext."
            return
        build_ext.run(self)


class post_install(install):
    def run(self):
        install.run(self)

        # on windows boxes, manually copy pre-compiled DLLs to
        # site-packages (or wherever the module is being installed)
        if "nt" in os.name:
            basedir = os.path.dirname(__file__)
            for f in glob.glob(os.path.join(basedir, "*.dll")):
                src = os.path.join(basedir, f)
                dst = os.path.join(self.install_lib, f)
                open(dst, "wb").write(open(src, "rb").read())

cHeatmap = Extension('cHeatmap', sources=['heatmap/heatmap.c', ])

setup(name='heatmap',
      version="2.2.1",
      description='Module to create heatmaps',
      author='Jeffrey J. Guy',
      author_email='jjg@case.edu',
      url='http://jjguy.com/heatmap/',
      license='MIT License',
      packages=['heatmap', ],
      py_modules=['heatmap.colorschemes', ],
      ext_modules=[cHeatmap, ],
      cmdclass={'install': post_install,
                'build_ext': mybuild},
      requires=["Pillow"],
      install_requires = ['Pillow'],
      extras_require = {'proj' : 'pyproj'},
      test_suite="test",
      tests_require=['pyproj'],
      )
