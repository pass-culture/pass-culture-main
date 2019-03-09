import withLogin from 'with-login'

export const withRedirectToSigninWhenNotAuthenticated = withLogin({
  failRedirect: ({ location }) =>
    `/connexion?de=${encodeURIComponent(
      `${location.pathname}${location.search}`
    )}`,
  isRequired: true,
})

export default withRedirectToSigninWhenNotAuthenticated
