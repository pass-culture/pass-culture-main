import { Selector } from 'testcafe'

import { createUserRole } from './roles'

export const HOME_URL = '/accueil'

export const navigateToHomeAs = (user, userRole) => async t => {
  const homepageNavItem = Selector('.nav-item').withText('Accueil')

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }
  await t.click(homepageNavItem)
}

export const navigateToOffersAs = user => async t => {
  const offersMenuItem = Selector("a[role='menuitem']").withText('Offres')

  await t.useRole(createUserRole(user))
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

  creationOrModification === 'creation'
    ? await t.expect(location.pathname).eql(HOME_URL)
    : await t
        .expect(location.pathname)
        .match(/\/structures\/([A-Z0-9]*)\/lieux\/([A-Z0-9]*)$/)

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

      if (userRole) {
        await t.useRole(userRole).click(newOfferAnchor)
      } else {
        await t.useRole(createUserRole(user)).click(newOfferAnchor)
      }
      await t.click(nextStepAnchor)
    }
  }

export const navigateToOfferAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const offerAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/edition"]`
  ).withText(offer.name)

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }

  await t.navigateTo('/offres')

  await t
    .typeText(searchInput, offer.name)
    .click(submitButton)
    .click(offerAnchor)
}

export const navigateToStocksAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const stocksAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/stocks"]`
  ).withText('Stocks')

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }

  await t.navigateTo('/offres')

  await t
    .typeText(searchInput, offer.name)
    .click(submitButton)
    .click(stocksAnchor)
}

export const navigateToNewMediationAs = (user, offer, userRole) => async t => {
  const addMediationAnchor = Selector('a').withText('Ajouter une accroche')

  await navigateToOfferAs(user, offer, userRole)(t)

  await t.click(addMediationAnchor)
}
