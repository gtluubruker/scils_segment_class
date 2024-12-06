from setuptools import setup

setup(name='scils_segment_class',
      version='0.2.0',
      description='SCiLS Python API workflow for segmenting SCiLS regions based on spatial connectivity.',
      url='https://github.com/gtluubruker/scils_segment_class',
      author='Gordon T. Luu',
      author_email='Gordon.Luu@Bruker.com',
      license='GPL-2.0 License',
      packages=['bin'],
      entry_points={'console_scripts': ['segment_class=bin.segment_class:main',
                                        'list_regions=bin.list_regions:list_regions']},
      install_requires=['numpy', 'pandas', 'scikit-image'])
