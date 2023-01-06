import { Selector } from 'testcafe'

export const HOME_URL = '/accueil'

export const navigateToHomeAs = (user, userRole) => async t => {
  const homepageNavItem = Selector('.nav-item').withText('Accueil')

  await t.useRole(userRole)
  await t.click(homepageNavItem)
}

export const navigateToOffersAs = userRole => async t => {
  const offersMenuItem = Selector("a[role='menuitem']").withText('Offres')

  await t.useRole(userRole)
  await t.click(offersMenuItem)
}

export const navigateToNewOffererAs = (user, userRole) => async t => {
  await navigateToHomeAs(user, userRole)(t)

  const offererSelect = Selector('#offererId')
  const offererOption = offererSelect.find('option')

  await t
    .click(offererSelect)
    .click(offererOption.withText('+ Ajouter une structure'))
}

export const navigateToOffererAs = (user, offerer, userRole) => async t => {
  await navigateToHomeAs(user, userRole)(t)

  const offererSelect = Selector('#offererId')
  const offererOption = offererSelect.find('option')

  await t.click(offererSelect).click(offererOption.withText(offerer.name))
}

export const navigateAfterVenueSubmit = creationOrModification => async t => {
  const notificationSuccess = Selector('div')
    .withAttribute('data-testid', 'global-notification-success')
    .withText(
      'Lieu créé. Vous pouvez maintenant y\u00a0créer une offre, ou en importer automatiquement.'
    )
  const submitButton = Selector('button[type="submit"]')

  await t.click(submitButton)
  const location = await t.eval(() => window.location)

  const venueUrlRegexp = '/structures/([A-Z0-9]*)/lieux/([A-Z0-9]*)'
  const expectedUrl =
    creationOrModification === 'creation'
      ? venueUrlRegexp + '\\?modification$'
      : venueUrlRegexp + '$'
  await t.expect(location.pathname + location.search).match(RegExp(expectedUrl))
  await t.expect(notificationSuccess.exists).ok()
}

export const navigateToNewOfferV2As =
  (user, offerer, venue, userRole) => async t => {
    const nextStepAnchor = Selector('button').withText('Étape suivante')

    if (venue) {
      const venueWrapper = Selector('h3.h-card-title').withText(venue.name)

      const displayVenueStats = venueWrapper
        .parent('div.h-card-header-row')
        .find('button')

      const newOfferAnchor = venueWrapper
        .parent('div.h-card-inner')
        .find('.venue-stats')
        .find("a[href^='/offre/creation']")

      await navigateToOffererAs(user, offerer, userRole)(t)
      await t.click(displayVenueStats)
      await t.click(newOfferAnchor)
      await t.click(nextStepAnchor)
      return
    } else if (offerer) {
      const venueWrapper =
        Selector('h3.h-card-title').withText('Offres numériques')

      const displayVenueStats = venueWrapper
        .parent('div.h-card-header-row')
        .find('button')

      const newOfferAnchor = venueWrapper
        .parent('div.h-card-inner')
        .find('.venue-stats')
        .find("a[href^='/offre/creation']")

      await navigateToOffererAs(user, offerer, userRole)(t)
      await t.click(displayVenueStats)
      await t.click(newOfferAnchor)
      await t.click(nextStepAnchor)
      return
    } else {
      const newOfferAnchor = Selector("a[href^='/offre/creation']")

      await navigateToHomeAs(user, userRole)

      await t.useRole(userRole).click(newOfferAnchor)
      await t.click(nextStepAnchor)
    }
  }

export const navigateToNewIndividualOfferAs = userRole => async t => {
  await t.useRole(userRole)

  const createOfferButton = Selector('a').withText('Créer une offre')
  await t.click(createOfferButton)

  const startOfferCreation = Selector('button').withText('Étape suivante')
  await t.click(startOfferCreation)
}

export const navigateToOfferEditionAs = (user, offer, userRole) => async t => {
  await t.useRole(userRole)
  await t.navigateTo(`/offre/${offer.id}/individuel/edition`)
}

export const navigateToOfferDetailsAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const detailsAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/edition"]`
  ).withText('Modifier')
  const offerAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/recapitulatif"]`
  ).withText(offer.name)

  await t.useRole(userRole)

  await t.navigateTo('/offres')

  await t
    .typeText(searchInput, offer.name, { paste: true })
    .click(submitButton)
    .click(offerAnchor)
    .click(detailsAnchor)
}

export const navigateToStocksAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const stocksAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/stocks"]`
  ).withText('Stocks')

  await t.useRole(userRole)

  await t.navigateTo('/offres')

  await t
    .typeText(searchInput, offer.name, { paste: true })
    .click(submitButton)
    .click(stocksAnchor)
}
