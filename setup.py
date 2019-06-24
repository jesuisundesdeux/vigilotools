from setuptools import setup

setup(
    name='vigilotools',
    version='1.0',
    packages=['core'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        vgtool=core.cmd:cli
    ''',
)
