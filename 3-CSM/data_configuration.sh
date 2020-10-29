python3 manage.py migrate --run-syncdb
python3 manage.py shell < import_csv2DB.py 
python3 manage.py migrate