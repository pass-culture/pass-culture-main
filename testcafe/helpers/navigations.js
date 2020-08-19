import { Selector } from 'testcafe'

import { createUserRole } from './roles'

export const navigateToOfferersAs = (user, userRole) => async t => {
  const navbarAnchor = Selector('a.navbar-link, span.navbar-burger').filterVisible()
  const offerersNavbarAnchor = Selector("a.navbar-item[href='/structures']")

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }
  await t.click(navbarAnchor).click(offerersNavbarAnchor)
}

export const navigateToOffersAs = user => async t => {
  const navbarAnchor = Selector('a.navbar-link, span.navbar-burger').filterVisible()
  const offersNavbarAnchor = Selector("a.navbar-item[href='/offres']")

  await t.useRole(createUserRole(user))
  await t.click(navbarAnchor).click(offersNavbarAnchor)
}

export const navigateToNewOffererAs = (user, userRole) => async t => {
  await navigateToOfferersAs(user, userRole)(t)
  const newOffererAnchor = Selector("a.primary-button[href='/structures/creation']")

  await t.click(newOffererAnchor)
}

export const navigateToOffererAs = (user, offerer) => async t => {
  const searchInput = Selector('#search').find('input')
  const submitButton = Selector('button[type="submit"]')
  const offererAnchor = Selector('li.offerer-item').find(`a[href^="/structures/${offerer.id}"]`)

  await navigateToOfferersAs(user)(t)

  await t
    .typeText(searchInput, offerer.keywordsString)
    .click(submitButton)
    .click(offererAnchor)
}

export const navigateAfterVenueSubmit = creationOrModification => async t => {
  const closeAnchor = Selector('button.close').withText('OK')
  const notificationError = Selector('.notification.is-danger')
  const notificationSuccess = Selector('.notification.is-success')
  const submitButton = Selector('button[type="submit"]')
  const redirectUrl =
    creationOrModification === 'creation'
      ? /\/structures\/([A-Z0-9]*)$/
      : /\/structures\/([A-Z0-9]*)\/lieux\/([A-Z0-9]*)$/

  await t.click(submitButton)
  const location = await t.eval(() => window.location)

  await t
    .expect(location.pathname)
    .match(redirectUrl)
    .expect(notificationSuccess.innerText)
    .contains(
      'Lieu créé. Vous pouvez maintenant y créer une offre, ou en importer automatiquement.\n\nOK'
    )

  await t
    .click(closeAnchor)
    .expect(notificationError.exists)
    .notOk()
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
  const searchInput = Selector('#search')
  const submitButton = Selector('button[type="submit"]')
  const offerAnchor = Selector('li.offer-item').find(`a[href^="/offres/${offer.id}"]`)

  if (!userRole) {
    await t.useRole(createUserRole(user))
  } else {
    await t.useRole(userRole)
  }

  await t.navigateTo('/offres')

  await t
    .typeText(searchInput, offer.keywordsString)
    .click(submitButton)
    .click(offerAnchor)
}

export const navigateToNewMediationAs = (user, offer, userRole) => async t => {
  const addMediationAnchor = Selector('a.button').withText('Ajouter une accroche')

  await navigateToOfferAs(user, offer, userRole)(t)

  await t.click(addMediationAnchor)
}
