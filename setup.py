from setuptools import setup, find_packages

setup(
    name='APIMonitor',
    version='0.1.0',
    description='API Monitor For Lenovo EService',
    long_description='API Monitor For Lenovo EService',
    packages=find_packages(),
	package_dir={'APIMonitor': 'APIMonitor'},
    url='https://github.com/yangxy16/APIMonitor.git',
    license='MIT',
    author='yangxy16@lenovo.com',
    author_email='yangxy16@lenovo.com',
    platforms='posix',
	zip_safe=False,
	include_package_data=True,
    install_requires=['requests','zeep','redis-py-cluster'],
    keywords=['APIMonitor'],
	classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
)
