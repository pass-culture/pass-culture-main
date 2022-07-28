import { TrackPageViewParams } from '@datapunt/matomo-tracker-react/lib/types'
import jsSHA from 'jssha'

export const getAnonymisedUserId = (): string | null => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')

  if (token == null) {
    return null
  }

  const userEmail = getUserEmailFromToken(token)
  const shaObj = new jsSHA('SHA-256', 'TEXT')
  shaObj.update(userEmail)
  const hashedValue = shaObj.getHash('HEX')

  return hashedValue
}

const getUserEmailFromToken = (token: string): string => {
  const base64Payload = token.split('.')[1]
  const parsedTokenPayload = JSON.parse(window.atob(base64Payload))

  return parsedTokenPayload['mail']
}

export const trackPageViewHelper = (
  trackPageView: (
    trackPageViewParameters: TrackPageViewParams
  ) => void | undefined
): void => {
  const params = new URLSearchParams(window.location.search)
  const venueParam = params.get('venue')
  const siret = params.get('siret')

  const documentTitle = 'Homepage'
  const trackPageViewParameters = {
    documentTitle: documentTitle,
  }

  if (venueParam != null || siret != null) {
    trackPageViewParameters.documentTitle += ' - From venue map'
  }

  if (siret != null) {
    trackPageViewParameters['customDimensions'] = [
      {
        id: 1,
        value: siret,
      },
    ]
  } else if (venueParam != null) {
    trackPageViewParameters['customDimensions'] = [
      {
        id: 2,
        value: venueParam,
      },
    ]
  }

  trackPageView(trackPageViewParameters)
}
