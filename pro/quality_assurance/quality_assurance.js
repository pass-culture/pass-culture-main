import { Selector, t } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { createUserRole } from '../testcafe/helpers/roles'
import fetchSandbox from '../testcafe/helpers/sandboxes'

fixture('Quality Assurance,').page(ROOT_PATH)

test('captures d’écran de toutes les pages du site', async () => {
  await takeScreenshot('connexion')
  await takeScreenshot('mot-de-passe-perdu')
  await takeScreenshot('inscription')
  await takeScreenshot('inscription/confirmation')

  const { user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  await t.useRole(createUserRole(user))

  await takeScreenshot('404')
  await t
    .navigateTo('/accueil')
    .takeScreenshot(optionsOfScreenshot('accueil'))
    .click(Selector('button').withText('Fred Leopold'))
    .takeScreenshot(optionsOfScreenshot('menu'))
  const token = Selector('label').withText('Contremarque')
  await t
    .navigateTo('/guichet')
    .typeText(token, 'FAAKEE', { replace: true, paste: true })
    .takeScreenshot(optionsOfScreenshot('guichet-FAAKEE'))
  await t
    .navigateTo('/guichet')
    .typeText(token, '100004', { replace: true, paste: true })
    .takeScreenshot(optionsOfScreenshot('guichet'))
  await t
    .navigateTo('/offres')
    .click(Selector('input[type="checkbox"]'))
    .click(Selector('.field-date-end .period-filter-input'))
    .takeScreenshot(optionsOfScreenshot('offres'))
    .typeText(
      Selector('label').withText('Nom de l’offre ou ISBN'),
      'search without result',
      { paste: true }
    )
    .click(Selector('button').withText('Lancer la recherche'))
    .takeScreenshot(optionsOfScreenshot('offres-search-without-result'))
  await t
    .navigateTo('/offres')
    .click(Selector('table a'))
    .takeScreenshot(optionsOfScreenshot('offre-edition'))
    .click(Selector('.of-placeholder'))
    .click(Selector('.tna-toggle'))
    .takeScreenshot(optionsOfScreenshot('thumbnail-upload-from-computer'))
    .click(Selector('.thumbnail-dialog .bc-step:not(.active) a'))
    .takeScreenshot(optionsOfScreenshot('thumbnail-upload-from-url'))
    .typeText(
      Selector('.thumbnail-dialog .tnf-form input[name="url"]'),
      'https://pass.culture.fr/wp-content/uploads/2020/11/N_PASS_CULTURE_HD.png',
      { paste: true }
    )
    .click(Selector('.thumbnail-dialog .tnf-url-button'))
    .takeScreenshot(optionsOfScreenshot('image-credit-input'))
    .click(Selector('.thumbnail-dialog .tnd-actions .primary-button'))
    .takeScreenshot(optionsOfScreenshot('thumbnail-image-editor'))
    .click(Selector('.thumbnail-dialog .tnd-actions .primary-button'))
    .takeScreenshot(optionsOfScreenshot('thumbnail-preview'))
    .click(Selector('.thumbnail-dialog .tnd-actions .primary-button'))
    .click(Selector('a').withText('Stock et prix'))
    .takeScreenshot(optionsOfScreenshot('offre-stocks'))
  await t
    .navigateTo('/offres/creation')
    .click(Selector('select').withText('Choisir un type'))
    .click(Selector('select option').withText('Jeux - abonnements'))
    .typeText(
      Selector('label').withText("Titre de l'offre"),
      'Un titre d’offre',
      { paste: true }
    )
    .click(Selector('select').withText('Sélectionnez une structure'))
    .click(Selector('select option').withText('Club Dorothy'))
    .click(Selector('select').withText('Sélectionnez un lieu'))
    .click(Selector('select option').withText('Maison de la Brique'))
    .typeText(
      Selector('label').withText('URL d’accès à l’offre'),
      'https://example.com',
      { paste: true }
    )
    .click(Selector('input[name="noDisabilityCompliant"]'))
    .takeScreenshot(optionsOfScreenshot('offre-creation'))
    .click(Selector('button').withText('Enregistrer et passer aux stocks'))
    .click(Selector('button').withText('Ajouter un stock'))
    .takeScreenshot(optionsOfScreenshot('offre-stocks'))
    .click(Selector('button').withText('Enregistrer'))
    .takeScreenshot(optionsOfScreenshot('offre-confirmation'))
  await t
    .navigateTo('/reservations')
    .click(Selector('img[alt="Filtrer par statut"]'))
    .takeScreenshot(optionsOfScreenshot('reservations'))
    .typeText(
      Selector(`input[placeholder="Rechercher par nom d'offre"]`),
      'search without result',
      { paste: true }
    )
    .takeScreenshot(optionsOfScreenshot('reservations-search-without-result'))
  await t
    .navigateTo('/profil')
    .takeScreenshot(optionsOfScreenshot('profil'))
    .click(Selector('button').withText('Enregistrer'))
    .takeScreenshot(optionsOfScreenshot('profil-success-banner'))
  await t
    .navigateTo('/structures')
    .takeScreenshot(optionsOfScreenshot('structures'))
    .click(Selector('a').withText('Club Dorothy'))
    .takeScreenshot(optionsOfScreenshot('structure'))
    .click(Selector('a').withText('+ Ajouter un lieu'))
    .takeScreenshot(optionsOfScreenshot('lieu-creation'))
    .click(Selector('button').withText('Annuler'))
    .click(Selector('a').withText('Maison de la Brique'))
    .takeScreenshot(optionsOfScreenshot('lieu'))
    .click(Selector('a').withText('Modifier le lieu'))
    .takeScreenshot(optionsOfScreenshot('lieu-edition'))
  await takeScreenshot('structures?mots-cles=search-without-result')
  await takeScreenshot('structures/creation')
  await takeScreenshot('remboursements')
  // TODO: Pourquoi vois-je du JS ?
  await takeScreenshot('remboursements/detail')
})

const takeScreenshot = async path => {
  await t.navigateTo(`/${path}`).takeScreenshot(optionsOfScreenshot(path))
}

const optionsOfScreenshot = path => ({
  path: `branch/${path.replace(/(\/|\?|=)/g, '-')}.png`,
  fullPage: true,
})
