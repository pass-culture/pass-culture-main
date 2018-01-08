## Ontology

L'ontology se compose tout d'abord de deux types d'utilisateurs: des CLIENTS et des PROFESSIONNELS (de la culture). Chaque PROFESSIONNEL possède une entité *seller* et peuvent proposer des *offers* aux CLIENTS. Ceci consiste à proposer un *price* pour un certain groupe d'*événement* ou un *work*. Si le CLIENT accepte la transaction, ce dernier voit son carnet d'*orders* augmenter de ce dernier achat.

Pour connaître les préférences culturelles des CLIENTS, l'application pose des *questions* à ces derniers lors de son inscription.

## Data Structures
### Events (object)

#### Properties
+ `endDate` (string, required)
+ `location` (string, required)
+ `offerId` (string, required)
+ `startDate` (string, required)
### Offers (object)

#### Properties
+ `comment` (string)
+ `editionDate` (string, required)
+ `id` (string, required)
+ `name` (string, required)
+ `sellerId` (string, required)
+ `thumbnailUrl` (string)
+ `workId` (string, required)
### Prices (object)

#### Properties
+ `condition` (string, required)
+ `eventId` (string, required)
+ `value` (string, required)
### Questions (object)

#### Properties
+ `choices` (array[string], required)
### Sellers (object)

#### Properties
+ `location` (object, required)
+ `thumbnailUrl` (string)
### UserQuestionJoins (object)

#### Properties
+ `choiceIndex` (number, required)
+ `questionId` (string, required)
+ `userId` (string, required)
### Users (object)

#### Properties
+ `firstName` (string, required)
+ `lastName` (string, required)
### UserSellerJoins (object)

#### Properties
+ `sellerId` (string, required)
+ `userId` (string, required)
### Works (object)

#### Properties
+ `category` (string, required)
+ `composer` (string, required)
+ `date` (string, required)
+ `identifier` (string, required)
+ `name` (string, required)
+ `performer` (string, required)
+ `thumbnailUrl` (string)
