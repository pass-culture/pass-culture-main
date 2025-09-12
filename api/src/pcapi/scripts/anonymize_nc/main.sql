-- queries copied from api/src/pcapi/scripts/rebuild_staging/anonymize.sql
-- only the WHERE clauses were added to target NC users and venues

-- functions
CREATE OR REPLACE FUNCTION pg_temp.fake_first_name(id bigint)
  RETURNS TEXT AS $$
DECLARE
  -- Most used first names extracted from PC production database (used 200 times or more on 2022-10-14)
  -- This enables to test search by name in the backoffice with realistic data.
  first_names TEXT[] = ARRAY[
    'LEA', 'EMMA', 'MANON', 'LUCAS', 'Emma', 'THEO', 'HUGO', 'THOMAS', 'CAMILLE', 'CHLOE', 'ENZO', 'Enzo', 'Manon',
    'CLARA', 'Lucas', 'Camille', 'Clara', 'INES', 'Léa', 'MARIE', 'MAXIME', 'SARAH', 'MATHIS', 'Sarah', 'Hugo', 
    'Thomas', 'NATHAN', 'ALEXANDRE', 'CLEMENT', 'ANTOINE', 'Mathis', 'LOUIS', 'OCEANE', 'Nathan', 'Chloé', 'ANAIS',
    'ROMAIN', 'LEO', 'LUCIE', 'JULIE', 'JADE', 'Jade', 'ALEXIS', 'Lucie', 'TOM', 'PAUL', 'BAPTISTE', 'QUENTIN', 
    'MATHILDE', 'Tom', 'Marie', 'Louis', 'EVA', 'ARTHUR', 'LAURA', 'LISA', 'PAULINE', 'Maxime', 'Lola', 'NICOLAS',
    'Antoine', 'Alexandre', 'LOLA', 'Lisa', 'JULIETTE', 'AXEL', 'Julie', 'VALENTIN', 'Romane', 'Paul', 'Yanis',
    'Mathilde', 'Alexis', 'ROMANE', 'Théo', 'Eva', 'MATTEO', 'JULIEN', 'Arthur', 'JULES', 'YANIS', 'Baptiste', 
    'Quentin', 'Romain', 'JUSTINE', 'Juliette', 'LOUISE', 'MARINE', 'Laura', 'CHARLOTTE', 'RAPHAEL', 'Jules', 
    'Clément', 'PIERRE', 'Inès', 'Anaïs', 'CELIA', 'Axel', 'ZOE', 'Lilou', 'MATHEO', 'Louise', 'Noah', 'MAEVA',
    'JEANNE', 'NOEMIE', 'LENA', 'MAXENCE', 'ELISA', 'Océane', 'Pauline', 'Léo', 'LOU', 'ADRIEN', 'Nicolas', 'EMILIE',
    'VICTOR', 'BENJAMIN', 'Gabriel', 'Charlotte', 'MATHIEU', 'CLEMENCE', 'Jeanne', 'Lou', 'Valentin', 'FLORIAN', 'Zoé',
    'ALICE', 'Justine', 'MARGAUX', 'Mohamed', 'CORENTIN', 'MORGANE', 'Maxence', 'GABRIEL', 'Julien', 'Lina', 'CARLA',
    'LILOU', 'Ines', 'Ethan', 'Ambre', 'Adam', 'NOAH', 'Pierre', 'ELISE', 'Raphaël', 'MARION', 'AMANDINE', 'SIMON', 
    'AMBRE', 'Evan', 'Mathéo', 'MARGOT', 'Noa', 'Alice', 'MELISSA', 'Victor', 'Elisa', 'Mathieu', 'MAELLE', 'Emilie',
    'KEVIN', 'ANTHONY', 'Marine', 'Célia', 'Adrien', 'MOHAMED', 'MARTIN', 'ALICIA', 'DYLAN', 'AGATHE', 'Benjamin', 
    'GUILLAUME', 'SAMUEL', 'Rayan', 'MAELYS', 'Clémence', 'Morgane', 'Léna', 'Alicia', 'Carla', 'AMELIE', 'TRISTAN',
    'BASTIEN', 'ETHAN', 'Noémie', 'Lea', 'ANNA', 'MAEL', 'DORIAN', 'EVAN', 'Sacha', 'Corentin', 'Simon', 'KILLIAN', 
    'Anna', 'Margot', 'Marion', 'Florian', 'Louna', 'Margaux', 'Elise', 'Theo', 'Samuel', 'RAYAN', 'ADAM', 'THIBAULT',
    'NOA', 'LINA', 'VINCENT', 'ELSA', 'MATTHIEU', 'Agathe', 'MATEO', 'NOE', 'VALENTINE', 'Nina', 'Martin', 'Amandine',
    'SACHA', 'Elsa', 'SOLENE', 'ANTONIN', 'ROBIN', 'REMI', 'FLAVIE', 'Yasmine', 'NINA', 'Maëlys', 'Dylan', 'ILONA',
    'Tristan', 'FANNY', 'Mathys', 'Kylian', 'KYLIAN', 'ELOISE', 'TITOUAN', 'JULIA', 'ANAELLE', 'ERWAN', 'AXELLE', 
    'Titouan', 'Maëlle', 'Mattéo', 'Amine', 'ELODIE', 'Sara', 'JEREMY', 'Bastien', 'Maël', 'LAURINE', 'Robin', 
    'Dorian', 'Nolan', 'SALOME', 'Matteo', 'Julia', 'LOUNA', 'MATHIAS', 'LOIC', 'Killian', 'Guillaume', 'Noé', 
    'ESTEBAN', 'Louane', 'MATHYS', 'DAMIEN', 'Candice', 'Anthony', 'Erwan', 'CLAIRE', 'CORALIE', 'ANDREA', 'YASMINE',
    'Chloe', 'AURELIEN', 'Mathias', 'Esteban', 'MEHDI', 'ALEXIA', 'CANDICE', 'AUDREY', 'Lana', 'LEANE', 'COLINE', 
    'Valentine', 'Antonin', 'CASSANDRA', 'Gabin', 'Fanny', 'LEONIE', 'Mehdi', 'LILIAN', 'YANN', 'Léane', 'Leo',
    'Thibault', 'Ilona', 'Matthieu', 'Raphael', 'Matheo', 'Luna', 'Lilian', 'GABIN', 'VICTORIA', 'ALIX', 'Anais', 
    'Amélie', 'EMELINE', 'WILLIAM', 'Mélissa', 'Maëva', 'MELANIE', 'Oceane', 'Loane', 'David', 'Flavie', 'Vincent', 
    'CHARLES', 'Yann', 'JORDAN', 'Lenny', 'DAVID', 'LOANE', 'Salomé', 'CLARISSE', 'JEAN', 'LENNY', 'Maeva', 'RYAN',
    'ADELE', 'William', 'Claire', 'LUNA', 'THIBAUT', 'ESTELLE', 'LISE', 'Cassandra', 'Sofia', 'CLEMENTINE', 'CLOE',
    'Lena', 'Sofiane', 'Axelle', 'Laurine', 'MELINA', 'MYRIAM', 'Coline', 'Clement', 'CAPUCINE', 'Myriam', 'Kevin',
    'LOUANE', 'SARA', 'AMINE', 'Alexia', 'Eloïse', 'Léonie', 'Enora', 'SOFIANE', 'HELOISE', 'Lise', 'Elodie', 'Marius',
    'NOLAN', 'Alix', 'Aya', 'ALEX', 'Damien', 'Victoria', 'Coralie', 'LUCILE', 'ENORA', 'Audrey', 'MARIUS', 'Yassine',
    'Eliott', 'ELIOTT', 'Anaëlle', 'Solène', 'ALEXANDRA', 'Capucine', 'BRYAN', 'Ryan', 'SOPHIE', 'GAETAN', 'ARNAUD',
    'Celia', 'AURELIE', 'LOGAN', 'Lucile', 'OLIVIA', 'LANA', 'Ayoub', 'Ninon', 'ETIENNE', 'Emeline', 'CAROLINE',
    'Lorenzo', 'Bilal', 'ALAN', 'LOAN', 'Salma', 'Lily', 'Rayane', 'Clarisse', 'Matéo', 'AUGUSTIN', 'Kenza', 'Olivia', 
    'ELENA', 'TANGUY', 'Rémi', 'Melissa', 'JONATHAN', 'PERRINE', 'SOFIA', 'Sophie', 'Imane', 'LORENZO', 'Rose', 'Malo',
    'Adèle', 'BILAL', 'CHARLINE', 'Jordan', 'YASSINE', 'GABRIELLE', 'UGO', 'MELINE', 'Gabrielle', 'KENZA', 'Alex', 
    'AURORE', 'SEBASTIEN', 'APOLLINE', 'Thibaut', 'Assia', 'LUDIVINE', 'Charles', 'ANGELE', 'BENOIT', 'ELEA', 'Maelys', 
    'Alexandra', 'AYMERIC', 'Faustine', 'Loïc', 'LUCA', 'ASSIA', 'Jean', 'Nassim', 'OSCAR', 'TONY', 'Cloé', 'MARINA', 
    'OPHELIE', 'RAYANE', 'Hamza', 'Flora', 'Clémentine', 'REMY', 'LAURE', 'Lila', 'Elias', 'ELIAS', 'MAILYS', 'Estelle', 
    'SALMA', 'EMILIEN', 'Loan', 'Oscar', 'IMANE', 'FLORA', 'KILIAN', 'Méline', 'Maya', 'NASSIM', 'MALO', 'Alan', 
    'Aurélien', 'Mael', 'Ewen', 'RACHEL', 'ROSE', 'NOLWENN', 'Bryan', 'ANISSA', 'TIMOTHEE', 'FAUSTINE', 'CELINE', 
    'LILA', 'ELEONORE', 'Ilyes', 'JESSICA', 'Andréa', 'Gaspard', 'Lou-Anne', 'Walid', 'GREGOIRE', 'CONSTANCE', 
    'LAETITIA', 'Lou-Ann', 'LAURYNE', 'VICTOIRE', 'CASSANDRE', 'KYLLIAN', 'Perrine', 'FRANCOIS', 'Mélanie', 'ALBAN', 
    'LUKAS', 'ALIZEE', 'Rachel', 'FABIEN', 'GASPARD', 'ANGELINA', 'Alyssa', 'FLORENT', 'SAMY', 'Mélina', 'Noemie', 
    'YANNIS', 'Amel', 'MATTHIAS', 'Charline', 'ALYSSA', 'Morgan', 'Chiara', 'FIONA', 'LORIS', 'YOUNES', 'Aurore', 
    'Lukas', 'Héloïse', 'LILY', 'Caroline', 'DIMITRI', 'Elena', 'Diego', 'LEILA', 'EWEN', 'Amina', 'ALLAN', 'AYOUB', 
    'Samy', 'YACINE', 'Elouan', 'Arnaud', 'Maelle', 'MORGAN', 'ORLANE', 'CHIARA', 'FELIX', 'MAUD', 'TIMOTHE', 
    'Rania', 'Ilan', 'Yacine', 'Noam', 'Luca', 'Selma', 'Timéo', 'Marina', 'Alban', 'TIPHAINE', 'Zoe', 'Jonathan',
    'Ahmed', 'GARANCE', 'Ibrahim', 'Jessica', 'NINON', 'JOSEPHINE', 'Manel', 'Lison', 'ELIOT', 'ILYES', 'Johan',
    'Kilian', 'Apolline', 'Youssef', 'EVE', 'LIAM', 'Ali', 'Kévin', 'MELVIN', 'Tony', 'FLORINE', 'Jérémy', 'Fatima', 
    'KELLY', 'Maud', 'Anissa', 'Yannis', 'Laure', 'JORIS', 'Sasha', 'SABRINA', 'YOHAN', 'Nora', 'CLEA', 'Garance',
    'Sami', 'CEDRIC', 'CHAIMA', 'Liam', 'Zakaria', 'GAUTHIER', 'Ludivine', 'ENOLA', 'LISON', 'Maria', 'Etienne', 
    'Constance', 'MAIWENN', 'SAMI', 'Logan', 'Aymeric', 'Younes', 'AMAURY', 'CECILE', 'Kyllian', 'MATIS', 'Mariam',
    'MICKAEL', 'BRICE', 'ORIANE', 'Kelly', 'Augustin', 'Cassandre', 'JUSTIN', 'Sabrina', 'Orlane', 'Angèle', 
    'Clemence', 'TEO', 'Ewan', 'JOHAN', 'Eliot', 'Luka', 'THAIS', 'Wassim', 'YOANN', 'GAELLE', 'STEVEN', 'JULIAN',
    'Elina', 'Mateo', 'Emilien', 'WALID', 'HAMZA', 'STELLA', 'AMEL', 'JASON', 'Timothée', 'ELOUAN', 'Lilia', 'GAEL',
    'Loris', 'Lyna', 'Ruben', 'PABLO', 'Victoire', 'Julian', 'Matis', 'Anouk', 'CYRIL', 'FLAVIEN', 'Angelina',
    'Daniel', 'DIEGO', 'NOAM', 'Dimitri', 'EWAN', 'Fatoumata', 'Céline', 'Lili', 'Oriane', 'DOUNIA', 'Emmy', 'Eden',
    'Nino', 'JOSEPH', 'LUC', 'Nour', 'SAMANTHA', 'SELMA', 'Stella', 'Anis', 'Pablo', 'Justin', 'DIANE', 'EDOUARD',
    'Thaïs', 'AMINA', 'Maïlys', 'HELENE', 'RANIA', 'Aurélie', 'Matthias', 'Shana', 'CYPRIEN', 'Lara', 'Marwa',
    'Sirine', 'ALI', 'Fabien', 'MARC', 'OLIVIER', 'Andrea', 'SIRINE', 'Melvin', 'Emmanuel', 'Gauthier', 'Allan',
    'Tiphaine', 'Mila', 'Florent', 'Eve', 'EMILE', 'ARMAND', 'Enola', 'CHARLENE', 'Olivier', 'THIBAUD', 'ANOUK',
    'AYA', 'Rafael', 'SHANA', 'ROXANE', 'LOIS', 'LOUISON', 'Amaury', 'ELINA', 'Timothé', 'Diane', 'EMMANUEL', 'Tanguy',
    'LUDOVIC', 'Yohan', 'EMMY', 'ISMAEL', 'Joris', 'SERENA', 'Alizée', 'Marwan', 'Anas', 'LOU ANNE', 'Eléa', 'Marc',
    'LAURIE', 'LOU-ANNE', 'GREGORY', 'LAURIANE', 'RUBEN', 'Yoann', 'Roxane', 'XAVIER', 'AHMED', 'CECILIA', 'DEBORAH',
    'Esther', 'EUGENIE', 'MAYA', 'SASHA', 'Louison', 'Cécile', 'Florine', 'Sonia', 'LILIA', 'Aaron', 'Lalie', 'Ugo', 
    'MAYLIS', 'ROMAN', 'Fiona', 'IRIS', 'LUCIEN', 'Aminata', 'FLORIANE', 'Joseph', 'Louanne', 'Lylou', 'TIFFANY',
    'NINO', 'NORA', 'BERENICE', 'Cléa', 'Iris', 'LILI', 'ASTRID', 'Jasmine', 'MILA', 'MAX', 'ADELINE', 'FABIO', 'ELIE',
    'IBRAHIM', 'Marilou', 'TESS', 'Anaelle', 'SONIA', 'François', 'Violette', 'HELENA', 'LARA', 'YOAN', 'Karim',
    'ERWANN', 'GWENDOLINE', 'Tess', 'Ana', 'Farah', 'Dounia', 'WENDY', 'Luc', 'NAWEL', 'Tessa', '', 'ANIS', 'LUKA',
    'YOUSSEF', 'EDEN', 'VIOLETTE', 'WASSIM', 'ZAKARIA', 'DANIEL', 'Steven', 'Emy', 'ALBANE', 'AURIANE', 'Laetitia',
    'LYNA', 'ILAN', 'Sébastien', 'CINDY', 'JIMMY', 'Cyprien', 'Jeremy', 'JOSHUA', 'Nolann', 'Hélène', 'Basile',
    'FARAH', 'KARIM', 'Laly', 'Tiago', 'LEANA', 'ANDY', 'BASILE', 'Mohammed', 'Omar', 'CLEO', 'Roman', 'AUDE',
    'CAMELIA', 'Léana', 'MARWAN', 'RAPHAELLE', 'ESTHER', 'Kenzo', 'ELLIOT', 'Nawel', 'AMELIA', 'MARIA', 'Armand',
    'Gaël', 'LUCY', 'Wendy', 'DAPHNE', 'Joshua', 'TATIANA', 'RAFAEL', 'Erwann', 'Sana', 'Eloise', 'ALINE', 'Gaëtan', 
    'Ilian', 'Loïs', 'Louka', 'MAE', 'Chaïma', 'Jason', 'Albane', 'CHRISTOPHER', 'Emile', 'Maïwenn', 'MARILOU', 'NOUR',
    'COME', 'Louann', 'Maylis', 'Cyril', 'Lucien', 'Moussa', 'TESSA', 'Louisa', 'NATHANAEL', 'Tatiana', 'JEREMIE', 
    'Owen', 'TIMEO', 'CELESTE', 'Elliot', 'Hajar', 'STANISLAS', 'FATOUMATA', 'Edouard', 'LOU-ANN', 'Lucy', 'Nolwenn',
    'MANEL', 'Yoan', 'GWENAELLE', 'Amira', 'LOUANNE', 'Paloma', 'HIPPOLYTE', 'Asma', 'Djibril', 'CORALINE', 
    'ANGELIQUE', 'Fabio', 'NAEL', 'PALOMA', 'Gwendoline', 'Léa ', 'VANESSA', 'Andy', 'Ilyas', 'MELODIE', 'ZELIE',
    'Elie', 'Eline', 'LEANDRE', 'Félix', 'MAXIMILIEN', 'TEDDY', 'ANNAELLE', 'Joséphine', 'Maïa', 'Nesrine', 'FARES',
    'FATIMA', 'YOHANN', 'Eléonore', 'Grégoire', 'SANA', 'OWEN', 'RONAN', 'Anne', 'DORIANE', 'Adeline', 'ALYCIA',
    'LUCILLE', 'Ludovic', 'Alycia', 'SYLVAIN', 'Ema', 'Melina', 'Téo', 'Aymen', 'Maéva', 'Rémy', 'Vanessa', 'SANDRA',
    'ADEL', 'JOHANNA', 'ERIC', 'Ophélie', 'ORNELLA', 'LOUANN', 'Naomie', 'Thibaud', 'EMA', 'Leila', 'MARIAM', 
    'MARIANNE', 'Brice', 'Chaima', 'COLIN', 'ROMEO', 'Amelie', 'FLORE', 'NAOMIE', 'Adel', 'Amir', 'CHARLY', 'MARVIN',
    'NAOMI', 'Adem', 'Lauryne', 'Max', 'Aline', 'Ayman', 'Leïla', 'Marylou', 'Solenn', 'Yousra', 'Angélina', 'Tiffany',
    'ANNE', 'CLOTILDE', 'Mamadou', 'THEOPHILE', 'Aude', 'STEPHANE', 'BRANDON', 'Chloé ', 'Flavien', 'AMIRA', 'Diana',
    'Leane', 'Maryam', 'Naomi', 'LEON', 'SOLENN', 'ALISON', 'MAUREEN', 'BLANDINE', 'Ismael', 'PHILIPPINE', 'REBECCA',
    'JASMINE', 'Jimmy', 'MARYLOU', 'ILIES', 'Sophia', 'CLELIA', 'GWENDAL', 'Zélie', 'EDGAR', 'LOUISA', 'Nils', 
    'Benoit', 'Samantha', 'SELENA', 'Lauriane', 'SOPHIA', 'MYLENE', 'Charly', 'EMMANUELLE', 'JENNIFER', 'Ismaël',
    'Milan', 'ASMA', 'BLANCHE', 'Sam', 'Suzanne', 'Xavier', 'Elia', 'KENZO', 'Marianne', 'MOHAMMED', 'Ronan', 'Sandra',
    'SUZANNE', 'ELINE', 'Ilias', 'MAISSA', 'Sylvain', 'ANATOLE', 'Flore', 'Maïssa', 'KASSANDRA', 'HENRI', 'LORIE',
    'Norah', 'Iman', 'MARIN', 'JESSY', 'THEA', 'Ange', 'DORINE', 'Swann', 'Bilel', 'NABIL', 'NESRINE', 'Philippe', 
    'SAM', 'Emmanuelle', 'Maé', 'Loic', 'LYLOU', 'LENY', 'Melvyn', 'Nabil', 'Anatole', 'Evann', 'Isaac', 'Christophe',
    'Gaëlle', 'Naël', 'CYNTHIA', 'GAUTIER', 'HORTENSE', 'ANA', 'GUILHEM', 'Ella', 'Malik', 'NILS', 'Ornella', 'Salim',
    'Solene', 'Céleste', 'Charlie', 'Cindy', 'CYRIELLE', 'LOUKA', 'Astrid', 'Côme', 'Daphné', 'Auriane', 'MARWA', 
    'ANGELINE', 'Isabelle', 'Lydia', 'ANGEL', 'DJIBRIL', 'LINDA', 'Marwane', 'Amélia', 'Eric', 'Léandre', 'PAOLA', 
    'ILIAN', 'Milo', 'Ulysse', 'ANAS', 'JEAN BAPTISTE', 'Cyrielle', 'IMENE', 'Alyssia', 'Johanna', 'LOU ANN', 'Marin',
    'ULYSSE', 'Charlène', 'MATTHEO', 'PHILIPPE', 'Blanche', 'ELLA', 'YAEL', 'LALIE', 'MELINDA', 'SWANN', 'VIRGILE',
    'clara', 'JEROME', 'Cédric', 'Noe', 'DONOVAN', 'ERINE', 'Leonie', 'Lucille', 'Reda', 'Bérénice', 'BILEL',
    'Yasmina', 'ALEXY', 'Clotilde', 'MELVYN', 'Fares', 'LEOPOLD', 'MAIA', 'Linda', 'LYDIA', 'EVANN', 'Clément ',
    'MATTHIS', 'Matys', 'ELIA', 'Kassandra', 'Timeo', 'Aurelien', 'emma', 'Laurent', 'Marvin', 'Achille', 'AICHA',
    'ALYSSIA', 'CHRISTOPHE', 'Colin', 'Remi', 'Ikram', 'Océane ', 'Cléo', 'ALEXANE', 'DELPHINE', 'Khadija', 'LINE',
    'MELODY', 'CELIAN', 'Loann', 'SOLINE', 'Yassin', 'EMY', 'PIERRICK', 'Cynthia', 'Eléna', 'Nadia', 'NOELIE',
    'YOUSRA', 'Cécilia', 'Erine', 'Jessy', 'Juline', 'Meriem', 'SAMIA', 'MOUSSA', 'Doriane', 'Edgar', 'ELOI', 'Elea',
    'Hippolyte', 'LEANNE', 'Bruno', 'SIXTINE', 'AARON', 'Christopher', 'Dina', 'Floriane', 'Hawa', 'Nathalie', 
    'Soraya', 'JULINE', 'REDA', 'SABRI', 'Line', 'MILAN', 'AMINATA', 'Samia', 'ANTONY', 'Jonas', 'ANGELO', 'EMERIC', 
    'Eugénie', 'FRANCK', 'Pierrick', 'SOFIAN', 'Teddy', 'ILYAS', 'LAURENT', 'JONAS', 'NATACHA', 'BERTILLE',
    'Nathanaël', 'Blandine', 'Joana', 'Jean-Baptiste', 'SORAYA', 'Tim', 'Angel', 'Camille ', 'Lindsay', 'STACY',
    'Léon', 'MARJORIE', 'MATISSE', 'Delphine', 'FLORENTIN', 'Gwendal', 'Hiba', 'LEONARD', 'Paolo', 'Fantine', 'Michel',
    'Rafaël', 'Rebecca', 'Yohann', 'Ismail', 'manon', 'KAIS', 'Malak', 'Joan', 'Paola', 'Jennifer', 'MALIK', 'MAMADOU',
    'SALIM', 'Clovis', 'Safia', 'LINDSAY', 'MARCO', 'Mina', 'Stanislas', 'ARIANE', 'LORINE', 'Marco', 'ACHILLE',
    'Elora', 'MARCEAU', 'Roméo', 'Ryad', 'THALIA', 'Hortense', 'AMIR', 'Mona', 'Leny', 'ANGE', 'CHARLIE', 'MATTIS',
    'Nael', 'PENELOPE', 'ADEM', 'ANNABELLE', 'Franck', 'KELIAN', 'SAFIA', 'Stéphane', 'Célian', 'Clélia', 'ELISABETH',
    'Guilhem', 'KENNY', 'JUDITH', 'NAIS', 'RUDY', 'Samir', 'TANIA', 'Angelo', 'Coraline', 'Idriss', 'Tania', 'ISAAC',
    'KIMBERLEY', 'Maureen', 'ORANE', 'Amin', 'EMRE', 'FREDERIC', 'ILIAS', 'LALY', 'MARYAM', 'Yuna', 'Anastasia',
    'Camélia', 'Thalia', 'Melanie', 'Syrine', 'Alexandre ', 'CESAR', 'Elio', 'Matisse', 'Yaël', 'ines', 'LOANN',
    'Marceau', 'MONA', 'OMAR', 'Lorine', 'HADRIEN', 'Kiara', 'Kim', 'MADISON', 'Théa', 'ALOIS', 'Miguel', 'Serena',
    'STEPHANIE', 'Alexy', 'ANASTASIA', 'Benoît', 'Cloe', 'Donovan', 'IMAN', 'LILAS', 'LOANNE', 'NAIM', 'Virgile',
    'YASMINA', 'Natacha', 'NOLANN', 'SAMIR', 'sarah', 'Stéphanie', 'Aïcha', 'AUBIN', 'Lilas', 'TIM', 'enzo', 'Loubna',
    'Stacy', 'ELORA', 'FLAVIO', 'Librairie', 'Manal', 'ALIENOR', 'Ylan', 'ELIO', 'LESLIE', 'MADELEINE', 'Leslie',
    'MAHE', 'YUNA', 'Raphaëlle', 'SIDONIE', 'TAMARA', 'GLADYS', 'ROSALIE', 'Thomas ', 'Alison', 'AURELIA', 'Flavio',
    'Grégory', 'Henri', 'LORENA', 'AYMEN', 'Brandon', 'GEOFFREY', 'IDRISS', 'Judith', 'MIA', 'MINA', 'Noham',
    'Alexane', 'Clementine', 'CLOTHILDE', 'FANTINE', 'HANNA', 'ISMAIL', 'KIM', 'Mattis', 'Maximilien', 'Mickaël', 
    'Nolhan', 'SANDY', 'ILHAN', 'MEGANE', 'NADIA', 'Aymane', 'Erika', 'Imen', 'IMEN', 'MAELINE', 'Naïs', 'NELL', 
    'Déborah', 'NEO', 'Safa', 'Tamara', 'Elisabeth', 'Kahina', 'LAUREEN', 'Nada', 'NORAH', 'YANNICK', 'YASSIN',
    'Annabelle', 'HECTOR', 'Hicham', 'Ilhan', 'Laurie', 'MAELIS', 'RYAD', 'Denis', 'Eleonore', 'Gaetan', 'Leelou', 
    'Lilly', 'PAOLO', 'Sabri', 'Mahé', 'Noha', 'Sofian', 'Soline', 'Angélique', 'Catherine', 'DINA', 'Ilana', 'Inès ',
    'Lubin', 'YAELLE', 'Antony', 'camille', 'ANAE', 'Marie-Lou', 'Matthis', 'MICHAEL', 'Sidonie', 'Gautier',
    'HONORINE', 'JACQUES', 'Sandy', 'Tina', 'Bertille', 'Jérémie', 'MILO', 'Nadir', 'Adele', 'Awa', 'Emie', 'ISABELLE',
    'Meline', 'DOMITILLE', 'ILANA', 'Issam', 'Léanne', 'Tao', 'BRIAN', 'Lohan', 'Mélodie', 'HANNAH', 'Aloïs', 'Ashley',
    'Jérôme', 'LYDIE', 'MARWANE', 'AMIN', 'Florence', 'MAELIE', 'Rudy', 'Imad', 'Jawad', 'Matthéo', 'Prune', 'YONI', 
    'Eloi', 'Florentin', 'Gael', 'MARGUERITE', 'Baptiste ', 'EMELYNE', 'Karl', 'MATYS', 'SHAIMA', 'Yasser', 'Abel',
    'Aicha', 'Aliya', 'Christian', 'Giovanni', 'Kenny', 'Nell', 'Noan', 'TYPHAINE', 'Youna', 'EMIE', 'ERIN', 
    'JEAN-BAPTISTE', 'Loanne', 'MATHILDA', 'Yoni', 'EGLANTINE', 'Mickael', 'Hanna', 'jade', 'LORIANE', 'GIOVANNI',
    'KAHINA', 'Kelyan', 'SEPHORA', 'SYRINE', 'Dorine', 'ERIKA', 'Giulia', 'Grace', 'HAJAR', 'SIHAM', 'Aubin', 'Hannah', 
    'HICHAM', 'lea', 'FLEUR', 'Johann', 'Lysa', 'LYSA', 'Riyad', 'Rosalie', 'CELESTINE', 'Emeric', 'Émilie', 'KARL',
    'Laureen', 'LOUBNA', 'Lya', 'Théo ', 'Elona', 'ISSAM', 'Kaïs', 'MARIO', 'Théophile', 'GIANNI', 'ISAURE', 'Issa', 
    'Nelson', 'ALEYNA', 'Alya', 'CLAUDIA', 'Fleur', 'Hector', 'Liza', 'Loriane', 'Patrick', 'ADELAIDE', 'BRUNO', 
    'Claudia', 'EDDY', 'JOANA', 'Lamia', 'Mariama', 'HAWA', 'Madison', 'SULLIVAN', 'Honorine', 'Ilies', 'JOHANN',
    'Kimberley', 'OMBELINE', 'Solal', 'Annaëlle', 'GRACE', 'Hana', 'Iliana', 'Jihane', 'Madeleine', 'Orane', 
    'Philippine', 'AYMAN', 'Frédéric', 'HAKIM', 'Klara', 'Maëline', 'Salome', 'Anaé', 'Camelia', 'JAWAD', 'Mailys',
    'Marouane', 'Maxim', 'MERIEM', 'Adama', 'Erin', 'LAURENE', 'Youcef', 'Gladys', 'Hakim', 'Naïm', 'Shaïna', 
    'Sixtine', 'ZACHARIE', 'Adil', 'AGNES', 'Fanta', 'Yannick', 'Eglantine', 'Eulalie', 'Hind', 'JOAN', 'ABEL', 
    'Anton', 'Enes', 'MICHEL', 'ASHLEY', 'CALVIN', 'PRUNE', 'Dany', 'ELONA', 'Jibril', 'Sohane', 'THEODORE', 'Adrian',
    'Amelia', 'Clothilde', 'Khalil', 'Léonard', 'LIZA', 'Maissa', 'MANDY', 'Manon ', 'Mariana', 'DONIA', 'Lily-Rose',
    'RIYAD', 'TIFENN', 'Cameron', 'Christine', 'LEELOU', 'lucas', 'ILLONA', 'Ivan', 'Lucas ', 'SHAINA', 'CELYA',
    'KATIA', 'Brahim', 'Joachim', 'Manelle', 'TIAGO', 'Calvin', 'Fatou', 'IVAN', 'JOACHIM', 'LAMIA', 'LEIA',
    'Mathilde ', 'Zineb', 'Chris', 'Estéban', 'EULALIE', 'Felix', 'Mohamed-Amine', 'Ophelie', 'Paco', 'Samira',
    'Siham', 'SOHANE', 'Brian', 'Clara ', 'Emily', 'Marjorie', 'Mia', 'Thierry', 'Typhaine', 'YVAN', 'ARNO', 'Bintou',
    'CLOVIS', 'DIANA', 'EMILY', 'Halima', 'SELIM', 'ANGELA', 'Ariane', 'DENIS', 'hugo', 'Jacques', 'TOMMY', 'Virginie',
    'Achraf', 'Aleyna', 'Eloane', 'Elyes', 'Helena', 'ISALINE', 'Noélie', 'Ousmane', 'Sebastien', 'Séréna', 'YOUNA',
    'ADRIAN', 'Adriana', 'LOLITA', 'MAREVA', 'Meryem', 'NATHALIE', 'Oussama', 'Zacharie', 'DANY', 'Hadrien', 
    'VICTORINE', 'ANTON', 'DRISS', 'Gwenaëlle', 'Remy', 'TINA', 'Antoine ', 'Emre', 'ILIANA', 'Abdallah', 'James',
    'Luis', 'Romy', 'Christelle', 'Gianni', 'PIERRE LOUIS', 'TAO', 'ADIL', 'Angela', 'Lia', 'LOISE', 'LUBIN', 'NAELLE',
    'VIVIEN', 'Wissam'
  ];
  first_names_length int = 1779;
BEGIN
  RETURN first_names[(id % first_names_length)+1];
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_last_name(id bigint)
  RETURNS TEXT AS $$
DECLARE
  -- To keep data anonymized but be able to search from first name and last name with realistic data,
  -- we assign last names from the name of all rivers in France (list from Wikipedia)
  rivers TEXT[] = ARRAY[
    'Abloux', 'Acheneau', 'Acolin', 'Aër', 'Aff', 'Agout', 'Ailette', 'Aille', 'Ain', 'Ainan', 'Aire', 'Airin',
    'Airon', 'Aisne', 'Aixette', 'Alagnon', 'Albarine', 'Albe', 'Alène', 'Allaine', 'Allier', 'Allière', 'Allondon',
    'Almont', 'Alzette', 'Alzon', 'Amance', 'Amous', 'Ance', 'Ancre', 'Andelle', 'Andelot', 'Andlau', 'Andon', 'Ange',
    'Anglin', 'Anguison', 'Antenne', 'Apance', 'Arc', 'Arconce', 'Ardèche', 'Ardière', 'Ardour', 'Argenton', 'Argonce',
    'Ariège', 'Arize', 'Arly', 'Armalause', 'Armance', 'Armançon', 'Arn', 'Arnon', 'Arnoult', 'Aroffe', 'Aron',
    'Arrats', 'Arré', 'Arros', 'Arroux', 'Artuby', 'Arvan', 'Arve', 'Arz', 'Asco', 'Aube', 'Aubetin', 'Aubois',
    'Audeux', 'Augronne', 'Aujon', 'Aumance', 'Aunette', 'Aure', 'Aurence', 'Auron', 'Auroue', 'Aussoue', 'Authion',
    'Authre', 'Autize', 'Automne', 'Auvézère', 'Auxance', 'Auxois', 'Auze', 'Auzon', 'Auzoue', 'Avance', 'Aveyron',
    'Avre', 'Azergues', 'Baïse', 'Baïsole', 'Baize', 'Bandiat', 'Bar', 'Barbuise', 'Barguelonne', 'Barguelonnette',
    'Barse', 'Bartassec', 'Bayon ou Bayeux', 'Beaume', 'Beauze', 'Benaize', 'Bénovie', 'Bernesse', 'Béronnelle',
    'Bertrande', 'Bès', 'Besbre', 'Béthune', 'Beuvron', 'Bèze', 'Biaysse', 'Bidouze', 'Bienne', 'Bièvre', 'Bionne',
    'Biourière', 'Blaise', 'Bléone', 'Blies', 'Boëme', 'Boivre', 'Bonne', 'Bonnieure', 'Bono', 'Boralde Flaujaguèse',
    'Borne', 'Bouble', 'Bouleure', 'Boulogne', 'Bourbeuse', 'Bourbince', 'Bourbre', 'Bourdic', 'Bourne', 'Boutonne',
    'Bouzanne', 'Bradascou', 'Braize', 'Brame', 'Bras de Bronne', 'Braye', 'Brêche', 'Brême', 'Brenne', 'Brestalou',
    'Breuchin', 'Brévogne', 'Brezons', 'Brézou', 'Briance', 'Brionneau', 'Brivet', 'Bromme', 'Bruche', 'Bruxenelle',
    'Buëch', 'Cailly', 'Calavon', 'Cambre', 'Cance', 'Canche', 'Cantache', 'Caramy', 'Cauron', 'Cause ou Infernet',
    'Cazine', 'Célé', 'Celle', 'Céor', 'Céou', 'Cère', 'Cérou', 'Cesse', 'Cèze', 'Chalaronne', 'Chapeauroux',
    'Charentonne', 'Chasse', 'Chassezac', 'Chat Cros', 'Chavanon', 'Chée', 'Cher', 'Chéran', 'Chère', 'Chiers',
    'Choisille', 'Ciron', 'Cisse', 'Claie', 'Clain', 'Claise', 'Clarée', 'Clarence', 'Cligneux', 'Clouère', 'Coise',
    'Colagne', 'Côle', 'Colmont', 'Colombine', 'Combade', 'Combeauté', 'Côney', 'Conie', 'Conroy', 'Corrèze', 'Cosson',
    'Couarde', 'Couasnon', 'Coulazou', 'Cousances', 'Cousin', 'Couze Chambon', 'Couze Pavin', 'Credogne', 'Creuse',
    'Crieulon', 'Crueize', 'Crusnes', 'Cuisance', 'Cure', 'Cusancin', 'Dadalouze', 'Dadou', 'Dan', 'Dathée',
    'Dessoubre', 'Deûle', 'Dheune', 'Diane', 'Diège', 'Dive', 'Dive du Sud', 'Doire', 'Doller', 'Don', 'Dordogne',
    'Dore', 'Doron de Beaufort', 'Doron de Bozel', 'Doron des Allues', 'Doubs', 'Doueff', 'Dourbie', 'Dourdou',
    'Doustre', 'Doux', 'Douyne', 'Douze', 'Drac', 'Drac Blanc', 'Dragne', 'Dranse', 'Drôme', 'Dronne', 'Dropt',
    'Droude', 'Druance', 'Drugeon', 'Durance', 'Durgeon', 'Eau Blanche', 'Eau Bourde', 'Eau d''Olle', 'Eau Salée',
    'Écaillon', 'Échandon', 'Échez', 'Egvonne', 'Eichel', 'Elle', 'Epte', 'Erdre', 'Ernée', 'Erve', 'Esch', 'Esches',
    'Esque', 'Essonne', 'Estampon', 'Estéron', 'Etze', 'Eure', 'Ével', 'Èvre', 'Eygues', 'Eyrieux', 'Èze', 'Fecht',
    'Fenioux', 'Fensch', 'Ferrand', 'Feuillade', 'Fier', 'Fil de Gorges', 'Flamenne', 'Flûme', 'Fouzon', 'Fresquel',
    'Furan', 'Furans', 'Fure', 'Furon', 'Fusain', 'Gabas', 'Galaure', 'Garbet', 'Gard', 'Gardon d''Alès',
    'Gardon d''Anduze', 'Gartempe', 'Gave d''Aspe', 'Gave de Pau', 'Gave d''Oloron', 'Gave d''Ossau', 'Gélise',
    'Gères', 'Gers', 'Gesse', 'Gier', 'Giessen', 'Giffre', 'Gijou', 'Gimone', 'Girou', 'Gizia', 'Gland', 'Gloire',
    'Gondoire', 'Gosne', 'Goul', 'Gourgeonne', 'Grande Thonaise', 'Grand Morin', 'Gravona', 'Gresse', 'Grosne',
    'Guerge', 'Guiers', 'Guil', 'Guisane', 'Hallue', 'Helpe Majeure', 'Helpe Mineure', 'Hem', 'Hérisson', 'Hers-Mort',
    'Hers-Vif', 'Houille', 'Hozain', 'Huisne', 'Hyrôme', 'Ill', 'Ille', 'Inam', 'Indre', 'Indrois', 'Isac', 'Isch',
    'Isère', 'Isle', 'Isole', 'Issole', 'Iton', 'Ixeure', 'Jamagne', 'Jarret', 'Jeu', 'Joigne', 'Jordanne', 'Jouanne',
    'Juine', 'Kirneck', 'Laignes', 'Laize', 'Landion', 'Langladure', 'Lanterne', 'Largue', 'Lary', 'Lathan', 'Lauch',
    'Launette', 'Lavaldenan', 'Lawe', 'Layon', 'Lède', 'Léez', 'Leff', 'Lemboulas', 'Lembron', 'Lemme', 'Lendou',
    'Lère', 'Les Usses', 'Leysse', 'Lez', 'Lézarde', 'Lèze', 'Liamou', 'Lidoire', 'Lié', 'Liège', 'Lièpvrette',
    'Ligne', 'Lignon', 'Lignon du Forez', 'Lignon du Velay', 'Linon', 'Lison', 'Livenne', 'Lizaine', 'Lizonne',
    'Loing', 'Loir', 'Loiret', 'Loison', 'Lot', 'Loue', 'Louge', 'Loyre', 'Lozon', 'Lumansonesque', 'Lunain', 'Luy',
    'Luy de Béarn', 'Luy de France', 'Luynes', 'Luzège', 'Lys', 'Madine', 'Madon', 'Maine', 'Malsanne', 'Maltorne',
    'Mamoul', 'Marmande', 'Marne', 'Maronne', 'Marque', 'Mars', 'Maulde', 'Mauldre', 'Maumont', 'Mayenne', 'Menoge',
    'Méouzette', 'Merdereau', 'Merderet', 'Mère', 'Meu', 'Meurthe', 'Midouze', 'Mimente', 'Minette', 'Moder', 'Moine',
    'Montane', 'Morbras', 'Morge', 'Mortagne', 'Morthe', 'Moselle', 'Moselotte', 'Mouzon', 'Naïc', 'Nartuby', 'Naute',
    'Nauze', 'Nave', 'Né', 'Négron', 'Nère', 'Neste', 'Niche', 'Nied', 'Nièvre', 'Ninian', 'Nive', 'Nizerand',
    'Nohain', 'Noireau', 'Nonette', 'Noue', 'Nouère', 'Odon', 'Œil', 'Ognon', 'Oignin', 'Oir', 'Oise', 'Oison',
    'Orain', 'Orbiel', 'Orbieu', 'Orge', 'Oriège', 'Orillon', 'Ornain', 'Orne', 'Orne champenoise', 'Orne saosnoise',
    'Orthe', 'Osse', 'Othain', 'Ouanne', 'Ouche', 'Oudon', 'Ouette', 'Ougeotte', 'Ource', 'Ourcq', 'Ourse', 'Oust',
    'Ouvèze', 'OUvèze', 'Ouysse', 'Oyon', 'Ozanne', 'Oze', 'Ozerain', 'Panouille', 'Petit Buëch', 'Petite Baïse',
    'Petite Creuse', 'Petite Rhue', 'Petite Sauldre', 'Petite Thonaise', 'Petit Lay', 'Petit Morin', 'Piou', 'Plaine',
    'Queugne', 'Rabodeau', 'Raddon', 'Rahun', 'Ramel', 'Rance', 'Récourt', 'Rémarde', 'Rère', 'Restonica', 'Réveillon',
    'Reverotte', 'Reyssouze', 'Rhins', 'Rhone', 'Rhônelle', 'Rhue', 'Rimarde', 'Risle', 'Roanne', 'Rôge', 'Rognon',
    'Rohan', 'Roizonne', 'Romaine', 'Romanche', 'Romme', 'Roule Crottes', 'Rouvre', 'Rozeille', 'Ru de Gally',
    'Rupt de Mad', 'Saine', 'Saint-Bonnette', 'Saint-Niel', 'Saison', 'Salat', 'Salindrenque', 'Salleron', 'Salon',
    'Sambre', 'Sâne Morte', 'Sâne Vive', 'Sânon', 'Santoire', 'Saône', 'Saônelle', 'Sarrampion', 'Sarre', 'Sarthe',
    'Sasse', 'Sauer', 'Sauldre', 'Saulx', 'Sausseron', 'Save', 'Savoureuse', 'Scardon', 'Scarpe', 'Scey', 'Scheer',
    'Scye', 'Sédelle', 'Sègre', 'Seiche', 'Seille', 'Selle', 'Selves', 'Semène', 'Semine', 'Semme', 'Semnon', 'Semois',
    'Semouse', 'Senouire', 'Séoune', 'Serein', 'Serre', 'Sesserant', 'Seugne', 'Sévenne', 'Séveraisse', 'Sèves',
    'Sèvre Nantaise', 'Sevron', 'Siguer', 'Siniq', 'Sioule', 'Smagne', 'Solnan', 'Solre', 'Somme-Soude', 'Sor',
    'Sorgue', 'Sormonne', 'Sorne', 'Sornin', 'Souche', 'Souchon', 'Soudaine', 'Sou de Laroque', 'Sou de Val de Daigne',
    'Souleuvre', 'Souloise', 'Soulzon', 'Suippe', 'Sumène', 'Superbe', 'Suran', 'Surmelin', 'Tardes', 'Tardoire',
    'Tarentaine', 'Tarn', 'Tarnon', 'Tarsy', 'Tartuguié', 'Tarun', 'Taurion', 'Taute', 'Télhuet', 'Tenise', 'Tenu',
    'Ternin', 'Ternoise', 'Terrette', 'Thérain', 'Thérouanne', 'Thin', 'Thiou', 'Tholon', 'Thon', 'Thonne', 'Thoré',
    'Thouanne', 'Thouaret', 'Thouet', 'Thur', 'Tialle', 'Tille', 'Tinée', 'Torse', 'Tortonne', 'Touch', 'Tourmente',
    'Tourtoulloux', 'Touvre', 'Trévelo', 'Trézon', 'Triouzoune', 'Trois Doms', 'Tronçon', 'Trottebec', 'Truyère',
    'Ubaye', 'Ubayette', 'Udon', 'Ure', 'Vaige', 'Vair', 'Val du Breuil', 'Vallière', 'Valloirette', 'Valouse',
    'Valserine', 'Vanne', 'Varenne', 'Vaucouleurs', 'Vaudelle', 'Vauvise', 'Vauvre', 'Vaux', 'Vauxonne', 'Vèbre',
    'Vecchio', 'Vègre', 'Vence', 'Vendée', 'Véore', 'Verdon', 'Verdouble', 'Vère', 'Vernaison', 'Vert', 'Verzée',
    'Vesgre', 'Vesle', 'Vésubie', 'Veuve', 'Veyle', 'Veynon', 'Vézère', 'Vezouze', 'Vianon', 'Viaur', 'Vicdessos',
    'Vicoin', 'Vie', 'Vienne', 'Vière', 'Vimbelle', 'Vimeuse', 'Vincou', 'Vingeanne', 'Vioulou', 'Virène', 'Virenque',
    'Vis', 'Vistre', 'Voire', 'Voise', 'Volane ', 'Vologne', 'Vonne', 'Voueize', 'Vouge', 'Voulzie', 'Vouraie', 'Vrin',
    'Weiss', 'Wiseppe', 'Woigot', 'Yerre', 'Yerres', 'Yèvre', 'Yon', 'Yonne', 'Yron', 'Yvel', 'Yvette', 'Yzeron',
    'Zinsel du Nord', 'Zinsel du Sud', 'Zorn'
  ];
  rivers_length int = 773;
BEGIN
  -- avoid having names in alphabetical order with ids, so this mixes a little bit
  RETURN rivers[((id * id + id) % rivers_length)+1];
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_phone_number_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN '+336' || lpad(id::text, 8, '0');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_id_piece_number_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN lpad(id::text, 12, '0');
END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pg_temp.fake_phone_number_from_id(id BIGINT)
  RETURNS TEXT AS $$
BEGIN
  RETURN '+336' || lpad(id::text, 8, '0');
END; $$
LANGUAGE plpgsql;

-- user
UPDATE "user"
SET
    "email" = 'user' || "id" || '@anonymized.email',
    "password" = 'fake-hashed-password'::bytea,
    "firstName" = pg_temp.fake_first_name(id),
    "lastName" = pg_temp.fake_last_name(id),
    "dateOfBirth" = '01/01/2001',
    "validatedBirthDate" = case when "validatedBirthDate" is null then null else '2001-01-01'::timestamp end,
    "idPieceNumber" = case when "idPieceNumber" is null then null else pg_temp.fake_id_piece_number_from_id(id) end,
    "phoneNumber" = pg_temp.fake_phone_number_from_id(id)
WHERE id IN (
    SELECT "user".id
    FROM "user"
    JOIN user_offerer ON user_offerer."userId" = "user".id
    JOIN offerer ON offerer.id = user_offerer."offererId"
    WHERE offerer.siren LIKE 'NC%' OR offerer."postalCode" LIKE '988%'
)
;

-- venue
UPDATE venue
SET
  "dmsToken" = 'dms-token-' || id,
  "bookingEmail" = 'venue-' || id || '-booking-email@anonymized.email',
  "collectiveEmail" = 'venue-' || id || '-collective-email@anonymized.email',
  "collectivePhone" = pg_temp.fake_phone_number_from_id(id)
WHERE id IN (
    SELECT venue.id
    FROM venue
    JOIN offerer ON offerer.id = venue."managingOffererId"
    WHERE offerer.siren LIKE 'NC%' OR offerer."postalCode" LIKE '988%'
)
;
