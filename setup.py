from setuptools import setup, find_packages
from glob import glob

setup(
    name = 'aosss',
    packages = find_packages(),
<<<<<<< HEAD
    version = '0.17.1.4',
=======
    version = '0.16.10.13',
    include_package_data=True,
>>>>>>> 5a16bcd049f07cb61b0fe3399cd0ecbdd95d80f0
    license = 'GNU GPLv3',
    platforms = 'any',
    description = 'Adaptive Optics Systems Simulation Support',
    author = 'Julio Trevisan',
    author_email = 'juliotrevisan@gmail.com',
    url = 'https://github.com/trevisanj/aosss', # use the URL to the github repo
    keywords= ['astronomy' 'adaptive optics'],
    install_requires = ['numpy', 'scipy', 'astropy', 'matplotlib', 'fortranformat'],  # matplotlib never gets installed correctly by pip, but anyway...
    scripts = glob('scripts/*.py')  # Considers system scripts all .py files in 'scripts' directory
)
