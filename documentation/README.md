# API SWAGGER DOCUMENTATION

## Pré-requis

Nous utilisons le plugin [Flasgger](https://github.com/rochacbruno/flasgger) permettant de visualiser via une app Flask, les specifications écrites dans un fichier .json
Flasgger est un outil de visualisation de la doc, utilisant Swagger.

## Comment ajouter une nouvelle route ?

- Nous utilisons l'outil de visualisation de documentation [Swagger](https://swagger.io/docs/specification/2-0/basic-structure/)
- Nous suivons la specification [OpenAPI 2](https://github.com/OAI/OpenAPI-Specification/) pour construire nos fichiers .json 
(en attendant une mise à jour de flasgger qui sera totalement compatible avec la spec openAPI 3)

- [Un example](https://github.com/flasgger/flasgger/blob/master/examples/example_app.py)

## Visualiser la documentation

Lancer le serveur : `python api_doc.py`

L'application est visible sur [http://localhost:5000/documentation/swagger/](http://localhost:5000/documentation/swagger/)

## Tester les routes en local

Il est possible de tester les appels API en utilisant la fonction **TRY IT OUT** sur le serveur de documentation :
- Lancer le serveur `pc start-backend`
- Créer des données avec `pc sandbox -n industrial`

### Connexion via ApiKey

Cliquer sur Authorize et entrer l'api key suivante "Bearer MAX98A9UTUVQEQ3MS9ZY2A5924CMBMZQ5EFM3AA4RUPYTUB99YFA4AF4RU6EJYXM" dans la fenêtre qui s'ouvre puis cliquer sur Authorize pour identifier l'utilisateur.
Cliquer sur le verbe de la route, par exemple 'GET', pour voir les détails de la route.
Cliquer sur **TRY IT OUT**  en haut à droite.

Entrer l'une des contremarques ci-dessous puis cliquer sur **Execute** pour faire l'appel api.

###  Réponses attendues avec l'utilsateur spécifié plus haut et des token (contremarques)

- Réponse 200 avec le token 100003
- Réponse 410 avec le token 100005 
- Réponse 403 avec le token 100002

## Générer de de nouvelles api keys

- Ouvrir un terminal
- Utiliser cette fonction :
```shell
function generate_password {
echo $(LC_CTYPE=C < /dev/urandom tr -dc A-Za-z0-9 | head -c ${1:-64})}
```
- Puis la lancer
```shell script
 $ generate_password
 $ O3jJrdb3Q8xp0SjuqcEmXLfWugGixyCm6KyuAdLTYQyA9frpXsmwakDlpJh0ZR5G
 $ generate_password 128
 $ ldl4N74NlNkBKLVhPaAvfOYgR4aLiKDWIjMBOJxWeVDbwdLN5VfDjbi7gZtHcPqLw5VsQb72rfPEP3THq6rhBFTZGnHIl36U5hhIFSyVGRmTqbI91ytmK61AMUSLZOb9
 ```

- Ouvrir un terminal psql
```shell script
$ pc psql
```
- puis
```sql
INSERT INTO api_key ("offererId", value)
VALUES
(14, 'CXt8EEPiG79YeXYfAosAsirSN9qGRPEFbZxJPzz016W1IHZbw3Mibg7VmKZn3ukp'),
(15, 'iUODWiOIF15brBnmnfZz4xMzwDw4pu8ihtAiLpUHGv4UscKb5IA22PAPrqpApx9A'),
(16, 'QVaFair1v7je9qQvR8rBusw3mWIaFCZFTELuNHrNFglblsrcjWMVZ3iqCyftGGWy');
```
