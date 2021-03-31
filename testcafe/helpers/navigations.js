import { Selector } from 'testcafe'

import { createUserRole } from './roles'

export const navigateToOfferersAs = (user, userRole) => async t => {
  const dropdownMenu = Selector('button').withText(user.publicName).filterVisible()
  const offerersMenuItem = Selector("a[role='menuitem']").withText(/Structure[s]? juridique[s]?/)

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }
  await t.click(dropdownMenu).click(offerersMenuItem())
}

export const navigateToOffersAs = user => async t => {
  const offersMenuItem = Selector("a[role='menuitem']").withText('Offres')

  await t.useRole(createUserRole(user))
  await t.click(offersMenuItem)
}

export const navigateToNewOffererAs = (user, userRole) => async t => {
  await navigateToOfferersAs(user, userRole)(t)
  const newOffererAnchor = Selector('a').withText('Ajouter une structure')

  await t.click(newOffererAnchor)
}

export const navigateToOffererAs = (user, offerer) => async t => {
  const searchInput = Selector('#search').find('input')
  const submitButton = Selector('button[type="submit"]')
  const offererAnchor = Selector('li.offerer-item').find(`a[href^="/structures/${offerer.id}"]`)

  await navigateToOfferersAs(user)(t)

  await t.typeText(searchInput, offerer.keywordsString).click(submitButton).click(offererAnchor)
}

export const navigateAfterVenueSubmit = creationOrModification => async t => {
  const notificationSuccess = Selector('.notification-v2.is-success').withText(
    'Lieu créé. Vous pouvez maintenant y créer une offre, ou en importer automatiquement.'
  )
  const submitButton = Selector('button[type="submit"]')
  const redirectUrl =
    creationOrModification === 'creation'
      ? /\/structures\/([A-Z0-9]*)$/
      : /\/structures\/([A-Z0-9]*)\/lieux\/([A-Z0-9]*)$/

  await t.click(submitButton)
  const location = await t.eval(() => window.location)

  await t.expect(location.pathname).match(redirectUrl).expect(notificationSuccess.exists).ok()
}

export const navigateToNewOfferAs = (user, offerer, venue, userRole) => async t => {
  if (venue) {
    const newOfferAnchor = Selector("a[href^='/structures/']")
      .withText(venue.name)
      .parent('div.list-content')
      .find("a[href^='/offres/creation?lieu=']")

    await navigateToOffererAs(user, offerer)(t)

    await t.click(newOfferAnchor)
    return
  }
  if (offerer) {
    const newOfferAnchor = Selector("a[href^='/structures/']")
      .withText(offerer.name)
      .parent('div.list-content')
      .find("a[href^='/offres/creation?structure=']")

    await navigateToOfferersAs(user)(t)

    await t.click(newOfferAnchor)
    return
  }
  const newOfferAnchor = Selector("a[href^='/offres/creation']")

  if (userRole) {
    await t.useRole(userRole).click(newOfferAnchor)
  } else {
    await t.useRole(createUserRole(user)).click(newOfferAnchor)
  }
}

export const navigateToOfferAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const offerAnchor = Selector(`a[href^="/offres/${offer.id}/edition"]`).withText(offer.name)

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }

  await t.navigateTo('/offres')

  await t.typeText(searchInput, offer.name).click(submitButton).click(offerAnchor)
}

export const navigateToStocksAs = (user, offer, userRole) => async t => {
  const searchInput = Selector('#offre')
  const submitButton = Selector('button[type="submit"]')
  const stocksAnchor = Selector(`a[href^="/offres/${offer.id}/stocks"]`).withText('Stocks')

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }

  await t.navigateTo('/offres')

  await t.typeText(searchInput, offer.name).click(submitButton).click(stocksAnchor)
}

export const navigateToNewMediationAs = (user, offer, userRole) => async t => {
  const addMediationAnchor = Selector('a').withText('Ajouter une accroche')

  await navigateToOfferAs(user, offer, userRole)(t)

  await t.click(addMediationAnchor)
}
