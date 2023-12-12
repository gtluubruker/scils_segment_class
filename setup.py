from setuptools import setup

setup(name='scils_segment_class',
      version='0.1.3',
      description='SCiLS Python API workflow for segmenting SCiLS regions based on spatial connectivity.',
      url='https://github.com/gtluubruker/scils_segment_class',
      author='Gordon T. Luu',
      author_email='Gordon.Luu@Bruker.com',
      license='MIT License',
      packages=['bin'],
      entry_points={'console_scripts': ['segment_class=bin.scils_segment_class:main']},
      install_requires=['numpy', 'pandas', 'scikit-image'])
