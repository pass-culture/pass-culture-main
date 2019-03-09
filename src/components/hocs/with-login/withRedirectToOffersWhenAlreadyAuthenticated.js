import withLogin from 'with-login'

export const withRedirectToOffersWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: () => '/offres',
})

export default withRedirectToOffersWhenAlreadyAuthenticated
