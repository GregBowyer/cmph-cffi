from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build

__VERSION__ = '0.3.0'


def get_ext_modules():
    import cmph
    return [cmph.ffi.verifier.get_extension()]


class CFFIBuild(build):
    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        build.finalize_options(self)


class CFFIInstall(install):
    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        install.finalize_options(self)


setup(
    name='cmph-cffi',
    version=__VERSION__,
    description='CFFI enabled bindings to the CMPH library for' +
                'creating and using minimal perfect hashes',
    long_description=open('README.rst', 'r').read(),
    author='Greg Bowyer & Venkatesh Sharma',
    author_email='gbowyer@fastmail.co.uk & venkatesh@urx.com',
    url='http://github.com/URXtech/cmph-cffi/',
    packages=['cmph'],
    tests_require=['tox'],
    install_requires=['cffi>=0.8', 'six'],
    cmdclass={
        'build': CFFIBuild,
        'install': CFFIInstall,
    },
    setup_requires=['cffi>=0.8', 'six'],
    include_package_data=False,
    zip_safe=False,
    package_data={'cmph': ['*.py', '*.c', '*.h']},
    keywords=['cmph', 'mph'],
    license='LGPL-2.1 & MPL-1.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: ' +
        'GNU Lesser General Public License v2 or later (LGPLv2+)',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Intended Audience :: Developers',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
