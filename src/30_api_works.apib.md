## Œuvres [/works]

### Lister des œuvres [/works{?type}]

+ Parameters

  + type : book, movie, theater_representation (enum, required) - Indique le type d'œuvre souhaité

#### Lister toutes les œuvres [GET]

+ Request

+ Response 200 (application/json)
    + Attributes (array[Book])

+ Response 400 (application/json)
    + Body

            [
               {
                 "text": "Wrong"
                }
            ]

### Pour une œuvre en particulier [/works/{type}:{identifier}]

+ Parameters

  + type : book, movie, theater_representation (enum, required) - Indique le type de l'œuvre considéré
  + identifier : identifiant de l'œuvre. Pour les livres, c'est l'ISBN. Pour les types d'œuvres pour lesquels il n'existe pas ce type d'identifiant unique, c'est un identifiant unique (UUID) créé par l'API.

#### Obtenir les informations sur l'œuvre [GET]

+ Request

+ Response 200 (application/json)
    + Attributes (Book)
    
#### Images (Couverture d'un livre, Affiche d'une pièce de théatre ou d'un film…) [/world/{type}:{identifier}/thumb.jpg]

