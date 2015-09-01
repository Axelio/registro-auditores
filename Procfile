web: python manage.py collectstatic --noinput; gunicorn auditores_suscerte.wsgi; python manage.py syncdb; python manage.py migrate; python manage.py loaddata main/fixtures/* 
