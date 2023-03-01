from setuptools import setup, find_packages

# GDAL will be installed separately in the Dockerfile as it is problematic to install it here
setup(
    name="git_cv",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'tensorflow',
        'numpy',
        'scipy',
        'matplotlib',
        'scikit-learn',
        'pandas',
        'h5py',
        'einops',
        'scipy',
        'keras-tuner',
        'dask',
        'keras',
        'geopandas',
        'numpy',
        'albumentations',
        'tqdm',
        'scikit-image',
        'aiohttp',
        'pyyaml',
        'cached-property',
    ]
)