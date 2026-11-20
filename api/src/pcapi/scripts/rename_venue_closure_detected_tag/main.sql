update
    criterion
set
    name = 'Fermeture demandée le partenaire culturel', 
    description = 'La structure est censée être fermée mais ne l’est pas'
where
    name = 'closure_detected'
