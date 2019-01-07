import { ClientFunction, Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { youngUserRole } from './helpers/roles'
import { youngUser } from './helpers/users'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const userContactOk = Selector('#user-contact_ok')
const userEmail = Selector('#user-email')
const userEmailError = Selector('#user-email-error')
const userPassword = Selector('#user-password')
const userPasswordError = Selector('#user-password-error')
const userPublicName = Selector('#user-publicName')
const signInButton = Selector('.is-secondary')
const signUpButton = Selector('button.button.is-primary')

fixture('01_01 SignupPage Component | Je crée un compte utilisatrice').page(
  `${ROOT_PATH}inscription`
)

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {
  await t.click(signInButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
  await t
    .typeText(userEmail, youngUser.email)
    .wait(500)
    .expect(signUpButton.innerText)
    .eql('Créer')
  await t.expect(signUpButton.hasAttribute('disabled')).ok()
})

test('Je crée un compte et je suis redirigé·e vers la page /découverte', async t => {
  await t
    .typeText(userPublicName, youngUser.publicName)
    .typeText(userEmail, youngUser.email)
    .typeText(userPassword, youngUser.password)
  await t
    .click(userContactOk)
    .wait(1000)
    .click(signUpButton)
    .wait(500)

  await t.expect(getPageUrl()).contains('/decouverte', { timeout: 3000 })
})

fixture(
  "01_02 SignupPage | Création d'un compte utilisateur | Messages d'erreur lorsque les champs ne sont pas correctement remplis"
).page(`${ROOT_PATH}inscription`)

test('E-mail déjà présent dans la base et mot de passe invalide', async t => {
  await t
    .typeText(userPublicName, youngUser.publicName)
    .typeText(userEmail, youngUser.email)
    .typeText(userPassword, 'pas')
    .wait(1000)
    .click(userContactOk)
    .wait(1000)
    .click(signUpButton)
    .wait(1000)
  await t
    .expect(userPasswordError.innerText)
    .eql(
      '\nLe mot de passe doit faire au moins 12 caractères et contenir à minima 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;\n\n'
    )
    .typeText(userPassword, 'RTit.uioRZU.90')
    .click(signUpButton)
    .wait(2000)
  await t
    .expect(userEmailError.innerText)
    .eql('\nUn compte lié à cet email existe déjà\n\n')
})

test('E-mail non autorisé', async t => {
  await t
    .typeText(userPublicName, youngUser.publicName)
    .typeText(userEmail, 'test@test.fr')
    .typeText(userPassword, youngUser.password)
    .wait(1000)
    .click(userContactOk)
    .wait(1000)
    .click(signUpButton)
    .wait(1000)
  await t
    .expect(userEmailError.innerText)
    .eql("\nAdresse non autorisée pour l'expérimentation\n\n")
})

// RECHERCHE

fixture('O5_01_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 500 })
})

fixture(
  "O5_01_02 Recherche | Je me suis connecté·e | J'arrive sur la page de recherche | Header"
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche`)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

const headerTitle = Selector('header')
const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)

// HOME

test('Je vois le titre de la page', async t => {
  await t.expect(headerTitle.innerText).eql('Recherche\n')
})

test('Je ne vois pas le bouton retour', async t => {
  await t.expect(Selector('button.back-button').exists).notOk()
})

test('Je vois le champ de recherche par mot-clé', async t => {
  await t
  await t.expect(Selector('#search-page-keywords-field').exists).ok()
})

test("Le filtre de recherche existe et l'icône n'est pas activé", async t => {
  await t
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
})

test('Je vois 7 vignettes', async t => {
  // TODO Revoir
  const pictureButton = Selector('#button-nav-by-offer-type')
  await t.expect(pictureButton.count).eql(7)
})

test('Lorsque je clique sur la croix, je reviens à la page des offres', async t => {
  const closeButton = Selector('#search-close-button')

  await t
    .click(closeButton)
    .wait(500)
    .expect(getPageUrl())
    .contains('/decouverte', { timeout: 3000 })
})

fixture(
  'O5_01_03 Recherche | Je cherche des offres par catégories et navigue'
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche/`)
})

// j'ai des résultats de recherche
test("Je clique sur la vignette 'Lire' et je suis redirigé vers la page de résultats de la recherche", async t => {
  const buttonNavByOfferType = Selector('#button-nav-by-offer-type').withText(
    'Lire'
  )
  const backButton = Selector('button.back-button')

  await t
    .click(buttonNavByOfferType)
    .wait(500)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire', { timeout: 3000 })

    // Le titre du header change
    .expect(headerTitle.innerText)
    .eql('Recherche : résultats\n')

    // Le filtre apparaît comme activé
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter-active')

  // Je vois le bouton pour revenir à la home
  await t
    .expect(backButton.exists)
    .ok()

    // Je clique sur le bouton pour revenir à la home
    .click(backButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}recherche`, { timeout: 3000 })
})
