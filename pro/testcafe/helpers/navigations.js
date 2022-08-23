import { Selector } from 'testcafe'

import { isSummaryPageActive } from './features'

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
  const notificationSuccess = Selector('.notification.is-success').withText(
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

export const navigateToNewOfferAs =
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

export const navigateToOfferDetailsAs = (user, offer, userRole) => async t => {
  const useSummaryPage = await isSummaryPageActive()
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const detailsAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/edition"]`
  ).withText('Modifier')
  const offerAnchor = useSummaryPage
    ? Selector(
        `a[href^="/offre/${offer.id}/individuel/recapitulatif"]`
      ).withText(offer.name)
    : Selector(`a[href^="/offre/${offer.id}/individuel/edition"]`).withText(
        offer.name
      )

  await t.useRole(userRole)

  await t.navigateTo('/offres')

  useSummaryPage
    ? await t
        .typeText(searchInput, offer.name, { paste: true })
        .click(submitButton)
        .click(offerAnchor)
        .click(detailsAnchor)
    : await t
        .typeText(searchInput, offer.name, { paste: true })
        .click(submitButton)
        .click(offerAnchor)
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

export const navigateToNewMediationAs = (user, offer, userRole) => async t => {
  const addMediationAnchor = Selector('a').withText('Ajouter une accroche')

  await navigateToOfferAs(user, offer, userRole)(t)

  await t.click(addMediationAnchor)
}
