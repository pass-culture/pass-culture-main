export const CONSTANTS = {
  // signIn page //
  signIn: '/connexion',
  signUp: '/inscription',
  emailId: '#email',
  passwordId: '#password',
  forgotPasswordText: 'Mot de passe oublié',
  requestPasswordLink: '/demande-mot-de-passe',
  signInButton: 'Se connecter',
  signUpButton: 'Créer un compte',
  securityRecommendationsText: 'Consulter nos recommandations de sécurité',
  securityRecommendationsLink:
    'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte',
  termsAndConditionsProfessionalsText: 'CGU professionnels',
  termsAndConditionsProfessionalsLink:
    'https://pass.culture.fr/cgu-professionnels/',
  personalDataText: 'Charte des Données Personnelles',
  personalDataLink: 'https://pass.culture.fr/donnees-personnelles/',
  cookieManagementWindow: 'Gestion des cookies',
  emailErrorId: '#error-details-email',
  passwordErrorId: '#error-details-password',
  incorrectUsernameOrPasswordText: 'Identifiant ou mot de passe incorrect.',
  randomEmail: Date.now().toString() + '@passculture.app',
  randomPassword: Date.now().toString() + 'TestCypress!',
  emailProAccount: 'pro_adage_eligible@example.com',
  // signUp page //
  iAlreadyHaveAnAccountButton: 'J’ai déjà un compte',
  lastNameId: '#lastName',
  randomLastName: 'France',
  firstNameId: '#firstName',
  randomFirstName: 'LE PAX',
  phoneNumberId: '#phoneNumber',
  randomPhoneNumber: '600000000',
  // signUp confirmation page //
  signUpConfirmationLink: 'inscription/confirmation',
  // CRUD //
  post: 'POST',
  get: 'GET',
  //  API  //
  signUpApi: '/v2/users/signup/pro',
}
