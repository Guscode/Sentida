import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name = 'sentida',
    version = '0.5.1',
    author = "Esben Kran, Søren Orm, Jacob Aarup Dalsgaard, Gustav Aarup Lauridsen, Lars Kjartan Bacher Svendsen",
    author_email = "contact@esbenkc.com",
    description = "The Sentida Danish sentiment analysis package",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/guscode/sentida",
    # packages = ['sentida'],
    licence = 'CCBY-NC 3.0',
    packages=setuptools.find_packages(),
    include_package_data = True,
    keywords = 'Natural Language Processing Sentiment Analysis',
    classifiers = [
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         "Development Status :: 4 - Beta",
         "Intended Audience :: Science/Research",
         "Topic :: Scientific/Engineering"
    ],
    package_data = {"sentida":['aarup.csv', 'intensifier.csv'],},
)
