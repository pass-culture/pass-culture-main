import ra from 'ra-language-french'
import { TranslationMessages } from 'react-admin'

const messages: TranslationMessages = {
  ...ra,
  app: {
    name: 'Back Office',
  },
  menu: {
    usersTitle: 'Jeunes et grand public',
    beneficiary: 'Jeunes bénéficiaires ou à venir',
    users: 'Utilisateurs grand public',
    features: 'Features flipping',
    categories: 'Catégories et sous-catégories',
    prosTitle: 'Acteurs Culturels',
    pros: 'List des acteurs culturels',
    offersCategory: "Catégories et sous-catégories d'Offres",
    conformity: 'Règles de conformité',
    offerValidation: 'Validation des offres',
    roleManagement: 'Gestion des rôles',
  },
  searchBar: {
    name: 'rechercher',
    placeholder: 'Rechercher par nom, prénom, e-mail, téléphone',
  },
}

export default messages
