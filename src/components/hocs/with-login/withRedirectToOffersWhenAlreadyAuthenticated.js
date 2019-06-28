import withLogin from 'with-login'

export const withRedirectToOffersWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: ({ currentUser }) => {
    const { hasOffers, hasPhysicalVenues } = currentUser || {}
    return hasOffers || hasPhysicalVenues
  ? '/offres' : '/structures'
  },
})
