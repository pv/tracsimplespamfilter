from setuptools import find_packages, setup

setup(
    name='TracSimpleSpamFilter',
    version='0.1',
    author='Pauli Virtanen',
    author_email='pav@iki.fi',
    description = "Simple regex-based content spam filter for Trac",
    license = "BSD",
    packages = find_packages(exclude=['*.tests*']),
    package_data={'tracsimplespamfilter' : []},
    install_requires = [],
    entry_points = {
        'trac.plugins': [
            'tracsimplespamfilter = tracsimplespamfilter',
        ]    
    }
)
