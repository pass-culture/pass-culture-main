# Package `local_providers`

Un provider est un fournisseur de données extérieur au Pass Culture.
Il peut être appelé via une interface local_provider pour ajouter des stocks, des products, des offers ou autre à la base de données, liées à une venue via le venue_provider.

Qu'est ce qu'un local_provider ?
C'est un composant intermédiaire permettant de faire la liaison entre une venue et un provider.

La récupération des données (stock, products, offers, etc.) se fait par des /connectors (API, ftp, etc.) puis sont enregistrées, après traitement, dans notre base de données.

C'est un iterator, appelle le __next__ dans local_provider.py


Providable n'est pas utilse lorsqu'on a récupéré toujours les informations d'un objet:
méta données 
- id
- date de modification
- type

Est-ce que je connais cet objet ? Est-ce que j'ai besoin de le mettre à jour

## Deux attributs 

###  can_create 
Certains providers sont autorisés à créer des objets mais d'autres peuvent seulemenr faire des mises à jour.
Par exemple, TiteLive est à false pour le thing_thumbs

### name 

+ init methode

## Deux méthodes
### fill_object_attributes


### __next__

 ```python
 class TiteLiveStocks(LocalProvider):
  def __next__(self)
 ```


Ces deux attributs et ces deux méthodes permettent de créer un template local_provider minimal


## Créer un template de Local Provider, par exemple, Allociné

Pour récupérer par exemple les stocks via le provider Tite Live pour une venue.
Créer une nouvelle classe qui hérite de Class LocalProvider(Iterator)

 ```python
 class TiteLiveStocks(LocalProvider):
 ```

Les étapes 

0. Update Object

1. Récupérer les données 
    La récupération des données se fait dans le domaine `/domain/allocine.py` qui va utiliser un connector `connectors/api_allocine` pour faire un appel à l'api ou autre pour récupérer les données à traiter.
    Le provider peut renvoyer de la data plus de la pagination

2. Lister les objet chez le provider (iterator __next__)

3. Savoir si on connaît cet objet
    a. non -> on instancie un nouvel objet -> UPDATE
    b. oui -> cet objet est-il à jour ?
        i. Oui -> il ne se passe rien
        ii. NON -> UPDATE






### Iteration

Une fois ces données récupérées, on itère dessus via le `__next__`

On créé un un providable_info via la méthode `create_providable_info()`, c'est un objet transitoire qui ne persiste pas.

`def __next__(self) -> List[ProvidableInfo]:


 `for providable_infos in self:`
 appelle le __next__

 Deux options, créer ou mettre à jour via les fonctions héritées de /local_providers/local_provider`
 :
 - def _create_object()
 - def _handle_update()


 `Create_providable_info` 
 - produit(s)
 - offre(s)

### Sauvegarde

Tous les 1000 objet on appelle `save_chunk` (CHUNK_MAX_SIZE)

 - /models
 
 Cas particulier de Tite Live
 - référentiel de données
 - stock : venue Provider qui utilise le provider tite live
 
# Comment le jouer au quotidien ?

C'est la méthode `updateObjects()` qui initie le processus de récupération, traitement et enregistrement des données :
- via l'interface pro, lorsque l'user synchronise pour la première fois ses données
- via un cron qui vérifie chaque jour `/api/scripts/update_providables.py` qiu va utiliser `do_update()`




---- 
à trier

l.24 on regarde l'état chez nous via l'id du providable_info
on récupère la date

un cas particulier des données = les images

l.28 on sauvegarde

@abstractmethode  : obligation de les redéfinir

on appelle next(objet) et pas le __next__

un id unique côté Provider qui sera la clé, de notre donnée pivot entre notre base et la base du provider


cas particulier de TiteLive
- données reférentielles
- stock -> venueProvider qui utilisent le Provider Tite live
