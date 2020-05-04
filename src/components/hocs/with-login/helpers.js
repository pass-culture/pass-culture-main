export const DEFAULT_TYPEFORM_LOCATION = '/typeform'
const TUTORIALS_LOCATION = '/bienvenue'

export const getRedirectionPath = ({ currentUser }) => {
  const { needsToFillCulturalSurvey, needsToSeeTutorials } = currentUser || {}

  if (needsToFillCulturalSurvey) {
    return DEFAULT_TYPEFORM_LOCATION
  } else if (needsToSeeTutorials) {
    return TUTORIALS_LOCATION
  }
  return undefined
}

export const getRedirectToCurrentLocationOrDiscovery = ({ currentUser }) => {
  const { needsToFillCulturalSurvey } = currentUser || {}
  if (!needsToFillCulturalSurvey) {
    return '/decouverte'
  }
  return undefined
}
