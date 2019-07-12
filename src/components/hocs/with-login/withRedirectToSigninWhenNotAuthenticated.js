import withLogin from 'with-login'

const withRedirectToSigninWhenNotAuthenticated = withLogin({
  failRedirect: ({ location }) =>
    `/connexion?de=${encodeURIComponent(`${location.pathname}${location.search}`)}`,
  isRequired: true,
})

export default withRedirectToSigninWhenNotAuthenticated
