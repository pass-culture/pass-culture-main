"""add book_macro_section table
"""
import csv
from io import StringIO

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ffd6d7217351"
down_revision = "a108c3bf5e27"
branch_labels = None
depends_on = None


# export de la table coté data
CSV_SECTION_DATA = """macro_rayon,rayon
Jeunesse,documentaire jeunesse nature
Jeunesse,documentaire jeunesse
Jeunesse,documentaire jeunesse audio vidéo ou produits tva 20
Jeunesse,documentaire jeunesse géographie atlas
Jeunesse,documentaire jeunesse histoire
Jeunesse,documentaire jeunesse encyclopédies et dictionnaires
Jeunesse,documentaire jeunesse art et culture
Jeunesse,documentaire jeunesse religion
Jeunesse,documentaire jeunesse sciences
Jeunesse,documentaire jeunesse revues
Jeunesse,documentaires et activités d'éveil pour la jeunesse
Jeunesse,littérature jeunesse romans / contes / fables poche
Jeunesse,littérature jeunesse romans / contes / fables
Jeunesse,jeunesse
Jeunesse,activité jeunesse 1er âge tva 5.5
Jeunesse,littérature jeunesse albums
Jeunesse,littérature jeunesse
Jeunesse,littérature jeunesse audio vidéo ou produits tva 20
Jeunesse,jeunesse en langue anglaise
Jeunesse,littérature jeunesse revues
Jeunesse,jeunesse en langue allemande
Bandes dessinées,bandes dessinées adultes / comics
Bandes dessinées,bandes dessinées jeunesse
Bandes dessinées,bandes dessinées
Bandes dessinées,bandes dessinées audio vidéo ou produits tva 20
Bandes dessinées,bandes dessinées revues
Bandes dessinées,bd et humour en langue anglaise
Bandes dessinées,bd et humour en langue allemande
Littérature française,littérature romans poche
Littérature française,poche revues
Littérature française,littérature française romans nouvelles correspondance
Littérature française,littérature française romans historiques
Littérature française,"littérature française récits, aventures, voyages"
Littérature française,littérature française
Littérature française,littérature française audio vidéo ou produits tva 20
Littérature française,littérature française romans régionaux
Littérature française,littérature française revues
Littérature française,romans au format poche
Littérature française,autobiographies contemporaines anthologies/dico
Littérature française,contes et légendes
Littérature française,petits prix
Littérature Etrangère,littérature étrangère
Littérature Etrangère,littérature étrangère audio vidéo ou produits tva 20
Littérature Etrangère,littérature asie (hors japon)
Littérature Etrangère,littérature moyen orient
Littérature Etrangère,littérature étrangère romans historiques
Littérature Etrangère,littérature japon
Littérature Etrangère,littérature afrique du nord
Littérature Etrangère,littérature en langue étrangère
Littérature Etrangère,littérature afrique noire
Littérature Etrangère,littérature étrangère revues
Littérature Etrangère,littérature afrique subsaharienne
 Droit,poche droit
 Droit,droit
 Droit,droit audio vidéo ou produits tva 20
 Droit,droit essais
 Droit,"droit public, droit administratif"
 Droit,droit constitutionnel
 Droit,droit fiscal
 Droit,relations et droit international
 Droit,droit civil et procédure civile
 Droit,droit pénal et procédure pénale
 Droit,droit commercial et des sociétés
 Droit,droit du travail et social
 Droit,droit pratique et correspondance
 Droit,histoire du droit et institutions publiques
 Droit,autres droits privés
 Droit,droit revues
 Droit,droit de l'urbanisme et environnement
 Droit,droit contrats types ou produits tva 20
Art,peinture / dessin d'art / gravure
Art,art en langue anglaise
Art,art et civilisation
Art,art religieux
Art,art en langue allemande
Art,sculpture
"Poèsie, théâtre et spectacle",poésie grand format
"Poèsie, théâtre et spectacle",poésie format poche
"Poèsie, théâtre et spectacle",arts et spectacle audio vidéo ou produits tva 20
"Poèsie, théâtre et spectacle",arts et spectacles
"Poèsie, théâtre et spectacle",théâtre
"Poèsie, théâtre et spectacle",poésie théâtre revues
"Poèsie, théâtre et spectacle",arts et spectacle revues
"Poèsie, théâtre et spectacle",poésie & théâtre
"Poèsie, théâtre et spectacle",poésie théâtre audio vidéo ou produits tva 20
 Arts Culinaires,produits pour la cuisine
 Arts Culinaires,arts de la table : recettes
 Arts Culinaires,cuisines étrangères
 Arts Culinaires,arts de la table
 Arts Culinaires,arts de la table audio vidéo ou produits tva 20
 Arts Culinaires,gastronomie et décoration de la table
 Arts Culinaires,arts de la table revues
 Tourisme,tourisme europe (hors france) guides
 Tourisme,tourisme france guides
 Tourisme,tourisme afrique guides
 Tourisme,tourisme asie / moyen-orient guides
 Tourisme,tourisme france livres
 Tourisme,tourisme océanie / pacifique guides
 Tourisme,tourisme amérique du nord / du sud guides
 Tourisme,tourisme & voyages livres
Tourisme,tourisme europe (hors france) livres
Tourisme,tourisme & voyage guides
Tourisme,"tourisme france cartes, plans, atlas routiers"
Tourisme,tourisme & voyages
Tourisme,voyages / tourisme / géographie en langue anglaise
Tourisme,tourisme cartes spécialisées
Tourisme,tourisme asie / moyen-orient livres
Tourisme,"tourisme & voyages (cartes, plans, atlas routiers,...)"
Tourisme,tourisme afrique livres
Tourisme,"tourisme amérique du nord / du sud cartes, plans, atlas routiers"
Tourisme,tourisme océanie / pacifique livres
Tourisme,tourisme amérique du nord / du sud livres
Tourisme,voyages / tourisme / géographie en langue allemande
Tourisme,"tourisme europe (hors france) cartes, plans, atlas routiers"
Tourisme,tourisme revues
Tourisme,"tourisme asie / moyen-orient cartes, plans, atlas routiers"
Tourisme,tourisme audio vidéo ou produits tva 20
Tourisme,"tourisme afrique cartes, plans, atlas routiers"
Tourisme,tourisme cartes marines
Tourisme,"tourisme océanie / pacifique cartes, plans, atlas routiers"
Littérature Europééne,littérature italienne
Littérature Europééne,littérature anglo-saxonne
Littérature Europééne,littérature hispano-portugaise
Littérature Europééne,littérature allemande
Littérature Europééne,littérature nordique
Littérature Europééne,littératures européennes rares
Littérature Europééne,anglais ouvrages de littérature
Littérature Europééne,espagnol ouvrages de littérature
Littérature Europééne,italien ouvrages de littérature
Littérature Europééne,allemand ouvrages de littérature
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique poche
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique audio vidéo ou produits tva 20
"Sciences Humaines, Encyclopédie, dictionnaire",textes et commentaires petits classiques
"Sciences Humaines, Encyclopédie, dictionnaire",poche philosophie
"Sciences Humaines, Encyclopédie, dictionnaire",philosophie
"Sciences Humaines, Encyclopédie, dictionnaire",philosophie audio vidéo ou produits tva 20
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique critiques et essais
"Sciences Humaines, Encyclopédie, dictionnaire",monographie / histoire de l'art / essais / dictionnaires
"Sciences Humaines, Encyclopédie, dictionnaire",philosophie dictionnaires et ouvrages généraux
"Sciences Humaines, Encyclopédie, dictionnaire",philosophie textes / critiques / essais / commentaires
"Sciences Humaines, Encyclopédie, dictionnaire",dictionnaires de langue française
"Sciences Humaines, Encyclopédie, dictionnaire",dictionnaires de langue française audio vidéo ou produits tva 20
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique dictionnaires et méthodes
"Sciences Humaines, Encyclopédie, dictionnaire",textes et commentaires
"Sciences Humaines, Encyclopédie, dictionnaire","médecine histoire, dictionnaires et essais"
"Sciences Humaines, Encyclopédie, dictionnaire",nature encyclopédie
"Sciences Humaines, Encyclopédie, dictionnaire",dictionnaires et atlas historiques
"Sciences Humaines, Encyclopédie, dictionnaire",géographie atlas et dictionnaires
"Sciences Humaines, Encyclopédie, dictionnaire",sociologie dictionnaires et lexiques
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique textes
"Sciences Humaines, Encyclopédie, dictionnaire",encyclopédies animales
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique revues
"Sciences Humaines, Encyclopédie, dictionnaire",philosophie revues
"Sciences Humaines, Encyclopédie, dictionnaire",lettres et linguistique latin grec
"Sciences Humaines, Encyclopédie, dictionnaire",santé et dictionnaires
"Sciences Humaines, Encyclopédie, dictionnaire",encyclopédies et autres religions
"Sciences Humaines, Encyclopédie, dictionnaire",textes et commentaires autres
"Sciences Humaines, Encyclopédie, dictionnaire",textes et commentaires littéraires et philosophiques
"Sciences Humaines, Encyclopédie, dictionnaire","sports encyclopédies, pédagogie, encyclopédies généralistes"
"Sciences Humaines, Encyclopédie, dictionnaire",dictionnaires spécialisés de langue française / divers
"Sciences Humaines, Encyclopédie, dictionnaire",encyclopédies
"Sciences Humaines, Encyclopédie, dictionnaire",dictionnaires de langue française revues
"Sciences Humaines, Encyclopédie, dictionnaire",epistémologie
Sexualité,littérature sentimentale poche
Sexualité,littérature érotique
Sexualité,sexualité
Sexualité,orientation
Sexualité,poche érotique
Informatique,informatique - internet
Informatique,informatique livres matériel et application mac
Informatique,informatique langages et programmation
Informatique,informatique bureautique
Informatique,informatique réseaux et internet
Informatique,informatique livres matériel p.c. et multimédia
Informatique,informatique systèmes d'exploitation
Informatique,informatique revues
Informatique,informatique audio vidéo ou produits tva 20
Informatique,informatique revues anglo saxonnes
Informatique,informatique / internet en langue anglaise
Informatique,informatique livres anglo saxon
Histoire,biographies historiques
Histoire,histoire de l'europe
Histoire,histoire
Histoire,poche histoire
Histoire,histoire audio vidéo ou produits tva 20
Histoire,histoire essais
Histoire,histoire du moyen age au 19ème siècle
Histoire,histoire du 20ème siècle à nos jours
Histoire,histoire revues
Histoire,histoire / actualité en langue anglaise
Histoire,histoire / actualité en langue allemande
Histoire,mythologie préhistoire antiquité et autres civilisations
Histoire,généalogie héraldique
"Sciences, vie & Nature",médecine (ouvrages de référence)
"Sciences, vie & Nature",faune revues
"Sciences, vie & Nature",sciences appliquées mathématiques
"Sciences, vie & Nature",médecine revues
"Sciences, vie & Nature",paramédical revues
"Sciences, vie & Nature",santé revues
"Sciences, vie & Nature","sciences de la vie et de la terre, botanique, ecologie"
"Sciences, vie & Nature",sciences politiques essais
"Sciences, vie & Nature",poche médecine
"Sciences, vie & Nature",médecine audio vidéo ou produits tva 20
"Sciences, vie & Nature","sciences appliquées astronomie, astrophysique"
"Sciences, vie & Nature",politique géopolitique
"Sciences, vie & Nature",sciences politiques
"Sciences, vie & Nature","sciences humaines (economie, psychologie, politique, droit, philosophie, art,..)"
"Sciences, vie & Nature",poches sciences appliquées
"Sciences, vie & Nature",sciences appliquées bâtiments et travaux publics
"Sciences, vie & Nature",médecines naturelles et parallèles
"Sciences, vie & Nature",sciences appliquées
"Sciences, vie & Nature",sciences appliquées audio vidéo ou produits tva 20
"Sciences, vie & Nature",sciences appliquées physique
"Sciences, vie & Nature",sciences appliquées electronique
"Sciences, vie & Nature",sciences appliquées chimie
"Sciences, vie & Nature","sciences appliquées agro-alimentaire, agronomie, agriculture"
"Sciences, vie & Nature",sciences appliquées revues
"Sciences, vie & Nature",médecine science fondamentale
"Sciences, vie & Nature",pharmacologie
"Sciences, vie & Nature",sciences politiques revues
"Sciences, vie & Nature",sciences / médecine en langue anglaise
"Sciences, vie & Nature",manuels de sciences politiques
"Sciences, vie & Nature",sciences humaines en langue anglaise
"Sciences, vie & Nature",internat et médecine interne
"Sciences, vie & Nature",sciences appliquées à la médecine
"Sciences, vie & Nature",sciences humaines en langue allemande
"Sciences, vie & Nature",sciences / médecine en langue allemande
"Sciences, vie & Nature",animaux domestiques et de compagnie
"Sciences, vie & Nature",nature
"Sciences, vie & Nature",nature audio vidéo ou produits tva 20
"Sciences, vie & Nature",jardinage
"Sciences, vie & Nature",faune
"Sciences, vie & Nature",faune audio vidéo ou produits tva 20
"Sciences, vie & Nature",oiseaux
"Sciences, vie & Nature",reptiles / batraciens / insectes
"Sciences, vie & Nature",petits élevages
"Sciences, vie & Nature",animaux sauvages
"Sciences, vie & Nature","roches, minéraux et fossiles"
"Sciences, vie & Nature",aquariophilie et faune aquatique
"Sciences, vie & Nature",champignons
"Sciences, vie & Nature",nature revues
Langue ,français langue étrangère lectures
Langue ,langues étrangères
Langue ,français langue étrangère
Langue ,allemand revues
Langue ,espagnol revues
Langue ,italien revues
Langue ,français langue étrangère audio vidéo ou produits tva 20
Langue ,français langue étrangère apprentissage
Langue ,autres langues méthodes livres
Langue ,autres langues ouvrages de littérature
Langue ,"langues rares (hors anglais, allemand, espagnol, italien, russe)"
Langue ,autres langues revues
Langue ,anglais  revues
Langue ,anglais enseignement supérieur
Langue ,espagnol enseignement supérieur
Langue ,allemand dictionnaires et guides de conversation
Langue ,italien dictionnaires et guides de conversation
Langue ,russe dictionnaires et guides de conversation
Langue ,espagnol dictionnaires et guides de conversation
Langue ,dictionnaires et guides de conversation
Langue ,autres langues dictionnaires et guides de conversation
Langue ,anglais (sans précision)
Langue ,italien (sans précision)
Langue ,anglais  audio vidéo ou produits tva 20
Langue ,méthodes langues
Langue ,espagnol (sans précision)
Langue ,autres langues enseignement supérieur
Langue ,français langue étrangère revues
Langue ,allemand enseignement supérieur
Langue ,revues en langue étrangère
Langue ,autres langues audio vidéo ou produits tva 20
Langue ,italien enseignement supérieur
Langue ,italien audio vidéo ou produits tva 20
Langue ,espagnol audio vidéo ou produits tva 20
Langue ,russe enseignement supérieur
Langue ,economie en langue anglaise
Langue ,allemand (sans précision)
Langue ,allemand audio vidéo ou produits tva 20
Langue ,anglais dictionnaires et guides de conversation
Langue ,scolaire en langue anglaise
Langue ,enseignement supérieur de langues étrangères
Langue ,"universitaire, ouvrages de références, essais, livres en langue étrangère"
Langue ,non attribué / foires aux livres
Langue ,anglais méthodes livres
Langue ,papeterie ou merchandising
Langue ,russe méthodes livres
Langue ,littérature russe
Langue ,espagnol méthodes livres
Langue ,allemand méthodes livres
Langue ,littérature collections de luxe
Langue ,italien méthodes livres
Langue ,qualité / production / logistique
Langue ,"supports hors livres & revues (k7,cd,...)en langue étrangère"
Langue ,rapports et planification française
Langue ,russe ouvrages de littérature
Langue ,russe revues
Langue ,russe (sans précision)
Langue ,russe audio vidéo ou produits tva 20
Economie,economie
Economie,poche economie
Economie,economie audio vidéo ou produits tva 20
Economie,comptabilité et finance
Economie,essais d'economie générale
Economie,théories et histoire économique
Economie,comptabilité générale et plans comptables
Economie,economie internationale
Economie,entreprise revues
Economie,expertise comptable
Economie,"gestion financière et fiscalité, bourse"
Economie,mathématiques économiques et financières
Economie,economie française
Economie,finances publiques
Economie,economie revues
Economie,comptabilité analytique
Economie,comptabilité revues
Economie,comptabilité audio vidéo ou produits tva 20
Scolaire & Parascolaire,manuels maternelles
Scolaire & Parascolaire,poche universitaire revuesenseignement universitaire revues
Scolaire & Parascolaire,pédagogie pour l'éducation
Scolaire & Parascolaire,poche encyclopédique non universitaire
Scolaire & Parascolaire,scolaire
Scolaire & Parascolaire,pédagogie
Scolaire & Parascolaire,pédagogie audio vidéo ou produits tva 20
Scolaire & Parascolaire,manuels maternelle et primaire
Scolaire & Parascolaire,sciences appliquées autres technologies
Scolaire & Parascolaire,enseignement universitaire
Scolaire & Parascolaire,enseignement universitaire audio vidéo ou produits tva 20
Scolaire & Parascolaire,autres enseignements techniques lycées professionnels
Scolaire & Parascolaire,manuels primaire audio vidéo ou produits tva 20
Scolaire & Parascolaire,manuels d'enseignement technique
Scolaire & Parascolaire,enseignement universitaire annales
Scolaire & Parascolaire,manuels lecture primaire
Scolaire & Parascolaire,techniques du mieux être
Scolaire & Parascolaire,manuels collège langues
Scolaire & Parascolaire,manuels langues primaire
Scolaire & Parascolaire,manuels d'enseignement tertiaire
Scolaire & Parascolaire,entraînement et soutien lycée
Scolaire & Parascolaire,manuels lycées français philosophie
Scolaire & Parascolaire,enseignement tertiaire cap bep
Scolaire & Parascolaire,poche universitaire encyclopédiques
Scolaire & Parascolaire,poche universitaire pluridisciplinaires
Scolaire & Parascolaire,manuels collège français
Scolaire & Parascolaire,manuels mathématiques primaire
Scolaire & Parascolaire,entraînement et soutien lycées techniques
Scolaire & Parascolaire,enseignement général cap bep
Scolaire & Parascolaire,entraînement et soutien collège
Scolaire & Parascolaire,manuels autres matières primaire
Scolaire & Parascolaire,annales collège
Scolaire & Parascolaire,annales lycées techniques
Scolaire & Parascolaire,manuels lycées d'enseignement général
Scolaire & Parascolaire,manuels français primaire
Scolaire & Parascolaire,annales lycée
Scolaire & Parascolaire,manuels histoire / géographie / instruction civique primaire
Scolaire & Parascolaire,manuels lycées langues vivantes
Scolaire & Parascolaire,manuels collège
Scolaire & Parascolaire,manuels collège audio vidéo ou produits tva 20
Scolaire & Parascolaire,autres enseignements techniques cap bep
Scolaire & Parascolaire,enseignement général lycées professionnels
Scolaire & Parascolaire,annales lycées professionnels
Scolaire & Parascolaire,manuels collège mathématiques
Scolaire & Parascolaire,manuels lycées audio vidéo ou produits tva 20
Scolaire & Parascolaire,manuels lycées mathématiques
Scolaire & Parascolaire,enseignement tertiaire lycées professionnels
Scolaire & Parascolaire,manuels lycées sciences économiques
Scolaire & Parascolaire,manuels collège histoire / géographie / instruction civique
Scolaire & Parascolaire,manuels collège latin grec
Scolaire & Parascolaire,manuels lycées latin grec
Scolaire & Parascolaire,manuels sciences et technologies primaire
Scolaire & Parascolaire,manuels lycées autres matières
Scolaire & Parascolaire,entraînement et soutien lycées professionnels
Scolaire & Parascolaire,manuels collège autres matières
Scolaire & Parascolaire,manuels lycées sciences physiques et chimie
Scolaire & Parascolaire,poche universitaire tertiaire
Scolaire & Parascolaire,autres enseignements techniques lycées techniques
Scolaire & Parascolaire,enseignement technique audio vidéo ou produits tva 20
Scolaire & Parascolaire,manuels collège sciences de la vie et de la terre
Scolaire & Parascolaire,sciences appliquées & livres techniques
Scolaire & Parascolaire,logiciel educatif
Scolaire & Parascolaire,manuels
Scolaire & Parascolaire,manuels lycées histoire / géographie
Scolaire & Parascolaire,annales cap bep
Scolaire & Parascolaire,manuels lycées sciences de la vie et de la terre
Scolaire & Parascolaire,pédagogie matériel tva 20
Scolaire & Parascolaire,enseignement général lycées techniques
Scolaire & Parascolaire,poche universitaire audio vidéo ou produits tva 20
Scolaire & Parascolaire,poche universitaire
Scolaire & Parascolaire,entraînement et soutien cap bep
Scolaire & Parascolaire,manuels d'enseignement industriel
Scolaire & Parascolaire,manuels collège sciences physiques
Scolaire & Parascolaire,enseignement industriel cap bep
Scolaire & Parascolaire,enseignement industriel lycées professionnels
Scolaire & Parascolaire,enseignement tertiaire lycées techniques
Scolaire & Parascolaire,soutien et entraînement
Scolaire & Parascolaire,enseignement industriel lycées techniques
Scolaire & Parascolaire,parascolaire technique
Scolaire & Parascolaire,esotérisme matériel tva 20
Scolaire & Parascolaire,enseignement technique revues
Scolaire & Parascolaire,manuels lycées revues
Scolaire & Parascolaire,enseignement
Scolaire & Parascolaire,poche universitaire industriel
Scolaire & Parascolaire,cahiers de vacances primaire
Scolaire & Parascolaire,cahiers de vacances maternelle
Scolaire & Parascolaire,cahier soutien primaire
Scolaire & Parascolaire,cahiers de vacances collège lycée
Scolaire & Parascolaire,parascolaire secondaire
Scolaire & Parascolaire,cahiers de vacances
Scolaire & Parascolaire,parascolaire primaire audio vidéo ou produits tva 20
Scolaire & Parascolaire,parascolaire primaire
Scolaire & Parascolaire,parascolaire secondaire revues
Scolaire & Parascolaire,parascolaire
Scolaire & Parascolaire,parascolaire maternelle audio vidéo ou produits tva 20
Scolaire & Parascolaire,parascolaire maternelle
"Faits, temoignages","sociologie faits de société, témoignages contemporains, actualité, biographies"
"Faits, temoignages","pamphlets politiques faits de société, témoignages, actualité, biographies"
"Faits, temoignages","médecine faits de société, témoignages contemporains, actualité, biographies"
"Faits, temoignages","droit faits de société, témoignages contemporains, actualité, biographies"
"Faits, temoignages","histoire faits de société, témoignages contemporains, actualité"
"Faits, temoignages","psychologie faits de société, témoignages récents, actualité, biographies"
"Faits, temoignages","sciences appliquées faits de société, témoignages contemporains, actualité, bio"
"Faits, temoignages","entreprise faits de société, témoignages contemporains, actualité, biographies"
"Faits, temoignages","informatique faits de société, témoignages contemporains, actualité, biographies"
"Faits, temoignages","economie faits de société, témoignages contemporains, actualité, biographies"
"Science-fiction, fantastique & terreur",science fiction / fantastique grand format
"Science-fiction, fantastique & terreur",science fiction / fantastique format poche
"Science-fiction, fantastique & terreur","fiction (hors poche) : romans, théâtre, poésie, humour..."
"Science-fiction, fantastique & terreur",science fiction / fantasy en langue anglaise
"Science-fiction, fantastique & terreur","fiction (poche) : romans, théâtre, poésie, humour..."
"Science-fiction, fantastique & terreur",science fiction / fantastique / terreur revues
"Science-fiction, fantastique & terreur",science fiction & terreur
"Science-fiction, fantastique & terreur",science fiction / fantastique / terreur audio vidéo ou produits tva 20
"Science-fiction, fantastique & terreur",science fiction & terreur (format poche)
"Science-fiction, fantastique & terreur",terreur grand format
"Science-fiction, fantastique & terreur",terreur format poche
Loisirs,loisirs auto / moto / avions / bateaux / trains
Loisirs,"mobilier, antiquités, design, décoration d'intérieur, métiers d'art"
Loisirs,"jardinage, bricolage, décoration, auto/moto"
Loisirs,"bricolage, jardinage, décoration, activités manuelles"
Loisirs,décoration
Loisirs,jeux revues
Loisirs,activité d'éveil jeunesse
Loisirs,activité d'éveil jeunesse cuisine
Loisirs,activités artistiques adulte
Loisirs,activité jeunesse livres objets tva 5.5
Loisirs,activités artistiques audio vidéo ou produits tva 20
Loisirs,activités artistiques
Loisirs,activités artistiques jeunesse
Loisirs,activité jeunesse jeux coloriages tva 5.5
Loisirs,activité jeunesse jeux coloriages ou produits tva 20
Loisirs,autre activité d'éveil jeunesse
Loisirs,loisirs audio vidéo ou produits tva 20
Loisirs,activité jeunesse audio vidéo ou produits tva 20
Loisirs,activité jeunesse livres objets ou produits tva 20
Loisirs,activités artistiques revues
Loisirs,activité jeunesse 1er âge ou produits tva 20
Loisirs,activité d'éveil jeunesse bricolage et jardinage
Loisirs,loisirs armes
Loisirs,loisirs revues
Loisirs,activité jeunesse revues
Loisirs,"art de vie, mode"
Loisirs,musique
Loisirs,photo
Loisirs,bricolage
Policier ,policier / thriller format poche
Policier ,policier / thriller grand format
Policier ,policier / suspense / espionnage en langue anglaise
Policier ,policier revues
Policier ,policier & thriller
Policier ,policier audio vidéo ou produits tva 20
Policier ,policier & thriller (format poche)
Gestion/entreprise,développement personnel
Gestion/entreprise,création d'entreprise
Gestion/entreprise,poche entreprise
Gestion/entreprise,entreprise
Gestion/entreprise,entreprise audio vidéo ou produits tva 20
Gestion/entreprise,management et ressources humaines
Gestion/entreprise,stratégie de l'entreprise
Gestion/entreprise,organisation des entreprises
Gestion/entreprise,contrôle de gestion
Jeux,jeux audio vidéo ou produits tva 20
Jeux,jeux
Jeux,jeux divers
Jeux,logiciel jeux
Jeux,jeux de société
Jeux,jeux de rôle
Vie pratique ,vie pratique & loisirs
Vie pratique ,randonnée survie
Vie pratique ,la vie après la mort
Vie pratique ,vie pratique en langue anglaise
Vie pratique ,vie pratique en langue allemande
Vie pratique ,logiciel vie pratique
Sport,"sports, equitation, tauromachie"
Sport,sports
Sport,sports revues
Sport,sports audio vidéo ou produits tva 20
Sport,sports mécaniques
Sport,sports collectifs
Sport,sports de montagne
Sport,sports individuels
Sport,sports nautiques
Sport,sports chasse / pêche
Sport,arts martiaux
Sport,gymnastique / sports d'entretien physique / danse
Sport,danses et autres spectacles
"Géographie, cartographie",géographie revues
"Géographie, cartographie","géographie, démographie, transports"
"Géographie, cartographie",géographie de la france
"Géographie, cartographie",poche géographie
"Géographie, cartographie",géographie audio vidéo ou produits tva 20
"Géographie, cartographie",géographie essais et études
"Géographie, cartographie",cartographie
"Géographie, cartographie",géographie de l'europe
"Géographie, cartographie",démographie
"Géographie, cartographie",histoire autres continents
"Géographie, cartographie",géographie autres continents
"Religions, spiritualitées",franc-maçonnerie / occultisme / symbolisme
"Religions, spiritualitées",religion revues
"Religions, spiritualitées",esotérisme revues
"Religions, spiritualitées",religion
"Religions, spiritualitées",poche religion
"Religions, spiritualitées",religion audio vidéo ou produits tva 20
"Religions, spiritualitées",phénomènes paranormaux et extraordinaires
"Religions, spiritualitées",maîtres spirituels / spiritualité
"Religions, spiritualitées",islam
"Religions, spiritualitées",orientalisme / bouddhisme / hindouisme
"Religions, spiritualitées","christianisme : essais religieux, témoignages, biographies"
"Religions, spiritualitées",christianisme : dictionnaires et théologie
"Religions, spiritualitées",judaïsme
"Religions, spiritualitées","spiritualité, esotérisme, religion"
"Religions, spiritualitées",biblesesotérisme
"Religions, spiritualitées",poche esotérisme
"Religions, spiritualitées",esotérisme audio vidéo ou produits tva 20
"Religions, spiritualitées",arts divinatoires
"Psychanalyse, psychologie",psychologie et psychanalyse poche
"Psychanalyse, psychologie",psychologie et psychanalyse audio vidéo ou produits tva 20
"Psychanalyse, psychologie",psychologie et psychanalyse
"Psychanalyse, psychologie",psychologie de l'enfant
"Psychanalyse, psychologie",psychologie / psychothérapie
"Psychanalyse, psychologie",psychanalyse
"Psychanalyse, psychologie",psychologie et psychanalyse revues
"Psychanalyse, psychologie",caractérologie graphologie morphologie
Manga,mangas / manwha / man hua
Carrière/Concours,carrières et emplois concours (hors professorat et paramédical)
Carrière/Concours,carrières et emplois
Carrière/Concours,carrières et emplois audio vidéo ou produits tva 20
Carrière/Concours,"pédagogie pour l'enseignement, concours professorat"
Carrière/Concours,recherche d'emploi
Carrière/Concours,"paramédical concours (infirmier, aide soignant, kiné, podologue, ...)"
Carrière/Concours,"carrière, travail, education"
Carrière/Concours,"conjugaison, grammaire, orthographe"
Carrière/Concours,carrières et emplois revues
Marketing et audio-visuel,"architecture, urbanisme, packaging, publicité"
Marketing et audio-visuel,"cinéma, télévision, audiovisuel, presse, médias"
Marketing et audio-visuel,"marketing, commercial, publicité"
Santé,santé & bien-être
Santé,flore et composition florale
Santé,"maternité, paternité, enfance"
Santé,vins et boissons
Santé,autres thèmes de santé
Santé,poche santé
Santé,santé audio vidéo ou produits tva 20
Santé,santé
Santé,aides soignants
Santé,arbres et arbustes
Santé,"alimentation, diététique, régimes"
Santé,infirmiers
Santé,autres spécialités médicales
Santé,kinés/podologues/ostéopathes
Santé,orthophonie et autres spécialités
Santé,chirurgie / traumatologie
Santé,homéopathie et autres médecines douces
Santé,vétérinaire
Santé,puériculture
Santé,paramédical
Santé,paramédical audio vidéo ou produits tva 20
Santé,soutien maternelle
Santé,soins dentaires / stomatologie
Santé,pédiatrie
Santé,radiologie / imagerie
Santé,pédagogie revues
Humour,humour grand format
Humour,humour format poche
Humour,humour audio vidéo ou produits tva 20
Humour,humour
Humour,humour revues
Sociologie,essais de sociologie
Sociologie,sociologie
Sociologie,sociologie audio vidéo ou produits tva 20
Sociologie,action sociale
Sociologie,sociologie traités/textes/auteurs fondamentaux
Sociologie,sociologie revues
Sociologie,ethnologie et anthropologie
"""


def _populate_from_csv(content):
    reader = csv.DictReader(StringIO(content))
    value_sets = []
    for row in reader:
        macro_section = row["macro_rayon"].replace("'", "''")  # escapes singles quotes for PG
        section = row["rayon"].replace("'", "''")  # escapes singles quotes for PG
        value_sets.append(f"('{macro_section}', '{section}')")
    op.execute('INSERT INTO book_macro_section("macroSection", section) ' f'VALUES {", ".join(value_sets)};')
    op.execute("COMMIT;")


def upgrade():
    op.create_table(
        "book_macro_section",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("macroSection", sa.Text(), nullable=False),
        sa.Column("section", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("section"),
    )
    _populate_from_csv(CSV_SECTION_DATA)


def downgrade():
    op.drop_table("book_macro_section")
