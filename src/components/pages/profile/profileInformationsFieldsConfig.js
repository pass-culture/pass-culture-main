import getDepartementByCode from '../../../utils/getDepartementByCode'
import IdentifiantForm from './forms/fields/UserIdentifierField'
import UserPasswordField from './forms/fields/UserPasswordField'

export const profileInformationsFieldsConfig = [
  // TODO: passer par une lib type https://github.com/yahoo/react-intl
  // pour gérer les pluralize et féminin des labels depuis un dictionnaire
  // FIXME -> ajouter une proptypes custom pour pouvoir vérifier dans les vues
  // que l'objet reçu pour les définitions des fields du formulaires est valide
  {
    component: IdentifiantForm,
    key: 'publicName',
    label: 'Identifiant',
    resolver: null,
    routeName: 'identifiant',
    title: 'Votre identifiant',
  },
  {
    // si la propriété `component` n'est pas définie
    // on considère la route comme disabled
    // component: ProfileFirstLastNameForm,
    // utilisé par le resolver
    // et la creation des items de type liste dans la vue main
    key: ['firstName', 'lastName'],
    // Utilisé pour afficher au dessus d'un field dans la vue main
    label: 'Nom et prénom',
    // ce champ est utile lorqu'on veut mettre un mainPlaceholder
    // dans la partie mes identifiants et qu'il n'y a pas de valeur par défaut
    mainPlaceholder: 'Renseigner mon nom et prénom',
    resolver: (user, [firstnameKey, lastnameKey]) =>
      [user[firstnameKey] || false, user[lastnameKey] || false].filter(v => v).join(' '),
    routeName: 'nom-prenom',
    title: 'Votre nom et prénom',
  },
  {
    key: 'email',
    label: 'Adresse e-mail',
    resolver: null,
    routeName: 'email',
    title: 'Votre adresse e-mail',
  },
  {
    component: UserPasswordField,
    key: 'password',
    label: 'Mot de passe',
    mainPlaceholder: 'Changer mon mot de passe',
    resolver: () => false,
    routeName: 'password',
    title: 'Votre mot de passe',
  },
  {
    key: 'departementCode',
    label: 'Département de résidence',
    resolver: (user, key) => {
      const code = user[key]
      const deptname = getDepartementByCode(code)
      return `${code} - ${deptname}`
    },
    routeName: 'departement',
    title: 'Votre Département de résidence',
  },
]
