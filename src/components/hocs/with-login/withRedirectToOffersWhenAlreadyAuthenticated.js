import withLogin from 'with-login'

export const withRedirectToOffersWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: ({ currentUser }) => {
     const { hasOffers } = currentUser || {}
    return hasOffers ? '/offres' : '/structures'
  },
})
