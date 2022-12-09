from setuptools import setup

setup(
    name="glite-info-update-endpoints",
    version="3.0.3",
    packages=["glite_info_update_endpoints"],
    entry_points={
        'console_scripts': [
            'glite-info-update-endpoints=glite_info_update_endpoints:main',
        ],
    },
)
