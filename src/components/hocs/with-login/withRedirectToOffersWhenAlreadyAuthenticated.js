import withLogin from 'with-login'

export const withRedirectToOffersWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: ({ currentUser }) => {
    const { hasOffers, hasPhysicalVenues } = currentUser || false
    const hasOffersWithPhysicalVenues = hasOffers && hasPhysicalVenues
    return hasOffersWithPhysicalVenues || hasPhysicalVenues ? '/offres' : '/structures'
  },
})
