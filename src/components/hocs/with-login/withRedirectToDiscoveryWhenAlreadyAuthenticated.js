import withLogin from 'with-login'

export const withRedirectToDiscoveryWhenAlreadyAuthenticated = withLogin({
  isRequired: false,
  successRedirect: () => '/decouverte',
})
