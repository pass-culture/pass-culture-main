# À vérifier

## Est-ce que l'utilisateur peut réserver plusieurs fois dans l'attente d'une réponse ?

Oui avec des curl par exemple, mais pas via l'app (ou j'ai pas réussi)

## Combien de connexions SQL par pods ?

Pour l'instance Postgres, `max_connections = 500`
Gunicorn est paramétré avec `GUNICORN_WORKERS=2`, `GUNICORN_THREADS=5`.
SQLAlchemy est paramétré avec `pool_size=20`, `max_overflow=10 (default)`
Donc si on a 10 pods :
10 * 2 * 20 = 400 connexions permanentes ?
Et au maximum (en cas de fort trafice) :
10 * 2 * (20 + 10) = 600 connexions