from setuptools import setup, find_packages

setup(
    name="glite-info-update-endpoints",
    version="3.0.1",
    py_modules=["glite_info_update_endpoints"], 
    entry_points={
        'console_scripts': [
            'glite-info-update-endpoints=glite_info_update_endpoints:main',
        ],
    },
)
