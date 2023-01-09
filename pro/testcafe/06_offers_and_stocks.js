import { Selector } from 'testcafe'

import { getPathname } from './helpers/location'
import { navigateToNewIndividualOfferAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const categoryInput = Selector('#categoryId')
const categoryOption = categoryInput.find('option')
const subcategoryInput = Selector('#subcategoryId')
const subcategoryOption = subcategoryInput.find('option')
const musicTypeInput = Selector('#musicType')
const musicTypeOption = musicTypeInput.find('option')
const musicSubTypeInput = Selector('#musicSubType')
const musicSubTypeOption = musicSubTypeInput.find('option')
const nameInput = Selector('#name')
const descriptionInput = Selector('#description')
const urlInput = Selector('#url')
const nextStep = Selector('button').withText('Étape suivante')
const saveOffer = Selector('button').withText('Enregistrer les modifications')
const createDraft = Selector('button').withText('Sauvegarder le brouillon')
const seeOffers = Selector('a').withText('Voir la liste des offres')
const modifyOffer = Selector('a').withText('Modifier')
const stocksPage = Selector('a').withText('Stock & Prix')
const publish = Selector('button').withText('Publier l’offre')
const beginninigDateInput = Selector('input').withAttribute(
  'placeholder',
  'JJ/MM/AAAA'
)
const beginninigTimeInput = Selector('input').withAttribute(
  'placeholder',
  'HH:MM'
)
const priceInput = Selector('input').withAttribute('data-testid', 'input-price')

fixture('En créant des offres et des stocks,').before(async ctx => {
  const { user, offerer, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  ctx.validatedUser = user
  ctx.offerer = offerer
  ctx.venue = venue
  const validatedUserRole = createUserRole(user)
  ctx.validatedUserRole = validatedUserRole
})

test('je peux créer & éditer une offre ou un brouillon événement physique et supprimer un stock', async t => {
  await navigateToNewIndividualOfferAs(t.fixtureCtx.validatedUserRole)(t)

  // on info
  await t
    .click(categoryInput)
    .click(categoryOption.withText('Cinéma'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Cinéma plein air'))
    .typeText(nameInput, 'Cinéma plein air', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/informations$/)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/stocks$/)

  // on stocks
  await t
    .click(priceInput)
    .typeText(priceInput, '2', { paste: true })
    .typeText(beginninigTimeInput, '20:37')
    .typeText(beginninigDateInput, '2222-11-03T05:00')
    .click(createDraft)
    .expect(getPathname())
    .match(/\/stocks$/)
    .click(priceInput)
    .typeText(priceInput, '21.31', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/recapitulatif$/)

  // on recap
  await t
    .click(publish)
    .expect(getPathname())
    .match(/\/confirmation$/)

  // can edit created offer
  const goToOffer = Selector('a').withText('Cinéma plein air')
  await t
    .click(seeOffers)
    .click(goToOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
    .click(modifyOffer)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(saveOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)

  // I can delete stock
  const accessDeleteButton = Selector('button[title="Opérations sur le stock"]')
  const deleteButton = Selector('span').withText('Supprimer le stock')
  const deleteSuccess = Selector('div')
    .withAttribute('data-testid', 'global-notification-success')
    .withText('Le stock a été supprimé.')

  await t
    .click(modifyOffer)
    .click(stocksPage)
    .click(accessDeleteButton)
    .click(deleteButton)
    .expect(deleteSuccess.exists)
    .ok()
})

test('je peux créer & éditer une offre ou un brouillon événement virtuel', async t => {
  await navigateToNewIndividualOfferAs(t.fixtureCtx.validatedUserRole)(t)

  // on info
  await t
    .click(categoryInput)
    .click(categoryOption.withText('Musique live'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Livestream musical'))
    .click(musicTypeInput)
    .click(musicTypeOption.withText('Blues'))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText('Blues Acoustique'))
    .typeText(nameInput, 'Livestream musical', { paste: true })
    .typeText(urlInput, 'https://example.com', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/informations$/)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/stocks$/)

  // on stocks
  await t
    .click(priceInput)
    .typeText(priceInput, '2', { paste: true })
    .typeText(beginninigTimeInput, '20:37')
    .typeText(beginninigDateInput, '2222-11-03T05:00')
    .click(createDraft)
    .expect(getPathname())
    .match(/\/stocks$/)
    .click(priceInput)
    .typeText(priceInput, '21.31', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/recapitulatif$/)

  // on recap
  await t
    .click(publish)
    .expect(getPathname())
    .match(/\/confirmation$/)

  // can edit created offer
  const goToOffer = Selector('a').withText('Livestream musical')
  await t
    .click(seeOffers)
    .click(goToOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
    .click(modifyOffer)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(saveOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
})

test('je peux créer & éditer une offre ou un brouillon objet physique', async t => {
  await navigateToNewIndividualOfferAs(t.fixtureCtx.validatedUserRole)(t)

  // on info
  await t
    .click(categoryInput)
    .click(categoryOption.withText('Beaux-arts'))
    .typeText(nameInput, 'Matériel arts créatifs', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/informations$/)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/stocks$/)

  // on stocks
  await t
    .click(priceInput)
    .typeText(priceInput, '2', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/stocks$/)
    .click(priceInput)
    .typeText(priceInput, '21.32', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/recapitulatif$/)

  // on recap
  await t
    .click(publish)
    .expect(getPathname())
    .match(/\/confirmation$/)

  // can edit created offer
  const goToOffer = Selector('a').withText('Matériel arts créatifs')
  await t
    .click(seeOffers)
    .click(goToOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
    .click(modifyOffer)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(saveOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
})

test('je peux créer & éditer une offre ou un brouillon objet virtuel', async t => {
  await navigateToNewIndividualOfferAs(t.fixtureCtx.validatedUserRole)(t)

  // on info
  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Abonnement plateforme streaming'))
    .typeText(nameInput, 'Abonnement plateforme streaming', { paste: true })
    .typeText(urlInput, 'https://example.com', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/informations$/)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/stocks$/)

  // on stocks
  await t
    .click(priceInput)
    .typeText(priceInput, '2', { paste: true })
    .click(createDraft)
    .expect(getPathname())
    .match(/\/stocks$/)
    .click(priceInput)
    .typeText(priceInput, '21.31', { paste: true })
    .click(nextStep)
    .expect(getPathname())
    .match(/\/recapitulatif$/)

  // on recap
  await t
    .click(publish)
    .expect(getPathname())
    .match(/\/confirmation$/)

  // can edit created offer
  const goToOffer = Selector('a').withText('Abonnement plateforme streaming')
  await t
    .click(seeOffers)
    .click(goToOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
    .click(modifyOffer)
    .typeText(descriptionInput, 'Description', { paste: true })
    .click(saveOffer)
    .expect(getPathname())
    .match(/\/recapitulatif$/)
})
