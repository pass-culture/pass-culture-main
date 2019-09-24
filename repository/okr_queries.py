import pandas


def get_all_experimentation_users_details():
    columns = ['Vague d\'expérimentation', 'Date d\'activation', 'Date de remplissage du typeform',
               'Date de première connection', 'Date de première réservation', 'Date de deuxième réservation',
               'Date de première réservation dans 3 catégories différentes', 'Date de dernière recommandation',
               'Nombre de réservations totales', 'Nombre de réservations non annulées']

    return pandas.DataFrame(columns=columns)
