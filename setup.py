import sys

from setuptools import find_packages, setup


needs_pylint = 'lint' in sys.argv
needs_pytest = bool({'pytest', 'test', 'ptr'}.intersection(sys.argv))
setuptools_lint = ['setuptools-lint'] if needs_pylint else []
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='gamebook',
    version='1.0',
    author='Eugen Zagorodniy',
    author_email='e.zagorodniy@gmail.com',
    description='Extract snap counts from NFL players',

    packages=find_packages(),
    python_requires='>=2.7,<3',
    install_requires=(
        'enum34',
        'lxml',
        'pdfminer',
        'psycopg2',
        'sqlalchemy',
    ),
    setup_requires=[] + pytest_runner + setuptools_lint,
    tests_require=(
        'pytest',
    ),
    entry_points = dict(
        console_scripts=(
            'gb-pdf-to-csv = gamebook:pdf_to_csv',
            'gb-url-to-csv = gamebook:url_to_csv',
            'gb-create-table = gamebook:create_table',
            'gb-url-to-db = gamebook:url_to_db',
        ),
    ),
)
