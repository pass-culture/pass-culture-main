import withLogin from 'with-login'

const DEFAULT_TYPEFORM_LOCATION = '/typeform'

export const getSuccessRedirection = ({ currentUser, location }) => {
  const { hasFilledCulturalSurvey } = currentUser || {}
  const currentLocation = `${location.pathname}${location.search}`
  return hasFilledCulturalSurvey ? currentLocation : DEFAULT_TYPEFORM_LOCATION
}

export const withRedirectToDiscoveryOrTypeForm = withLogin({
  isRequired: false,
  successRedirect: getSuccessRedirection,
})
