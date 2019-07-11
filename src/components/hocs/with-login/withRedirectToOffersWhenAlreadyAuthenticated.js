import withLogin from 'with-login'

export const redirectToUrl = (data) => {
  const { currentUser } = data
  const { hasOffers, hasPhysicalVenues } = currentUser || false
  const hasOffersWithPhysicalVenues = hasOffers && hasPhysicalVenues
  return hasOffersWithPhysicalVenues || hasPhysicalVenues ? '/offres' : '/structures'
}

export const withRedirectToOffersWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: redirectToUrl
})
