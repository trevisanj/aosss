from setuptools import setup, find_packages
from glob import glob

NAME = 'aosss'
setup(
    name =NAME,
    packages = find_packages(),
    version = '0.17.1.4',
    include_package_data=True,
    license = 'GNU GPLv3',
    platforms = 'any',
    description = 'Adaptive Optics Systems Simulation Support',
    author = 'Julio Trevisan',
    author_email = 'juliotrevisan@gmail.com',
    url = 'https://github.com/trevisanj/aosss', # use the URL to the github repo
    keywords= ['astronomy' 'adaptive optics'],
    install_requires = ['numpy', 'scipy', 'astropy', 'matplotlib', 'fortranformat'],  # matplotlib never gets installed correctly by pip, but anyway...
    scripts = glob(NAME+'/scripts/*.py')  # Considers system scripts all .py files in 'scripts' directory
)
