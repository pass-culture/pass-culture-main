## Ontologie

L'ontologie se compose tout d'abord de deux types d'utilisateurs: des CLIENTS et des PROFESSIONNELS (de la culture). Chaque PROFESSIONNEL possède une entité *seller* et peuvent proposer des *offers* aux CLIENTS. Ceci consiste à proposer un *price* pour un certain groupe d'*événement* ou un *work*. Si le CLIENT accepte la transaction, ce dernier voit son carnet d'*orders* augmenter de ce dernier achat.

Pour connaître les préférences culturelles des CLIENTS, l'application pose des *questions* à ces derniers lors de son inscription.

## Data Structures

### Event (object)

#### Properties
+ `endDate` (string, required)
+ `location` (string, required)
+ `offerId` (string, required)
+ `startDate` (string, required)

### Offer (object)

#### Properties
+ `comment` (string)
+ `editionDate` (string, required)
+ `id` (string, required)
+ `name` (string, required)
+ `sellerId` (string, required)
+ `thumbnailUrl` (string)
+ `workId` (string, required)

### Price (object)

#### Properties
+ `condition` (string, required)
+ `eventId` (string, required)
+ `value` (string, required)

### Question (object)

#### Properties
+ `choices` (array[string], required)

### Seller (object)

#### Properties
+ `location` (object, required)
+ `thumbnailUrl` (string)

### User (object)

#### Properties
+ `firstName` (string, required)
+ `lastName` (string, required)

### Work (object)

#### Properties
+ `category` (string, required)
+ `composer` (string, required)
+ `date` (string, required)
+ `identifier` (string, required)
+ `name` (string, required)
+ `performer` (string, optional)

#### Book (Work)

##### Properties
+ `category`: book (string, required)
+ `composer`: On Lisp (string, required)
+ `date`: 01/09/1993 (string, required)
+ `identifier`: 9780130305527 (string, required)
+ `name`: On Lisp (string, required)
+ `publisher`: Prentice Hall (string, required)
