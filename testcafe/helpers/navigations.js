import { Selector } from 'testcafe'

import { createUserRole } from './roles'

export const navigateToOfferersAs = user => async t => {
  const navbarAnchor = Selector(
    'a.navbar-link, span.navbar-burger'
  ).filterVisible()
  const offerersNavbarAnchor = Selector("a.navbar-item[href='/structures']")

  await t.useRole(createUserRole(user))
  await t.click(navbarAnchor).click(offerersNavbarAnchor)
}

export const navigateToNewOffererAs = user => async t => {
  const newOffererAnchor = Selector(
    "a.button.is-primary[href='/structures/creation']"
  )

  await navigateToOfferersAs(user)(t)

  await t.click(newOffererAnchor)
}

export const navigateToOffererAs = (user, offerer) => async t => {
  const searchInput = Selector('#search').find('input')
  const submitButton = Selector('button[type="submit"]')
  const offererAnchor = Selector('li.offerer-item').find(
    `a[href^="/structures/${offerer.id}"]`
  )

  await navigateToOfferersAs(user)(t)

  await t
    .typeText(searchInput, offerer.keywordsString)
    .click(submitButton)
    .click(offererAnchor)
}

export const navigateToNewVenueAs = (user, offerer) => async t => {
  const newVenueAnchor = Selector('a.button.is-secondary').withText(
    '+ Ajouter un lieu'
  )
  const offererAnchor = Selector("a[href^='/structures/']").withText(
    offerer.name
  )

  await navigateToOfferersAs(user)(t)

  await t.click(offererAnchor).click(newVenueAnchor)
}

export const navigateToVenueAs = (user, offerer, venue) => async t => {
  const offererAnchor = Selector("a[href^='/structures/']").withText(
    offerer.name
  )
  const venueAnchor = Selector("a[href^='/structures/']").withText(venue.name)

  await navigateToOfferersAs(user)(t)

  await t.click(offererAnchor).click(venueAnchor)
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

export const navigateToNewOfferAs = (user, offerer, venue) => async t => {
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
  await t.useRole(createUserRole(user)).click(newOfferAnchor)
}

export const navigateToOfferAs = (user, offer) => async t => {
  const searchInput = Selector('#search')
  const submitButton = Selector('button[type="submit"]')
  const offerAnchor = Selector('li.offer-item').find(
    `a[href^="/offres/${offer.id}"]`
  )

  await t.useRole(createUserRole(user))

  await t
    .typeText(searchInput, offer.keywordsString)
    .click(submitButton)
    .click(offerAnchor)
}

export const navigateToNewMediationAs = (user, offer) => async t => {
  const addMediationAnchor = Selector('a.button').withText(
    'Ajouter une accroche'
  )

  await navigateToOfferAs(user, offer)(t)

  await t.click(addMediationAnchor)
}
