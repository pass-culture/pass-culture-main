import { storageAvailable } from './storageAvailable'

export const SAVED_HOME_PAGE_VENUE_ID_KEYS = 'savedHomePageVenueIdKeys'
export const SAVED_PARTNER_PAGE_VENUE_ID_KEYS = 'savedPartnerPageVenueIdKeys'

type Context = 'homepage' | 'partnerPage'
type OffererId = number | string | undefined | null

const getSavedPartnerPageVenueId = (
  context: Context,
  offererId: OffererId
): string | undefined => {
  if (!offererId || !storageAvailable('localStorage')) {
    return
  }

  const key =
    context === 'homepage'
      ? SAVED_HOME_PAGE_VENUE_ID_KEYS
      : SAVED_PARTNER_PAGE_VENUE_ID_KEYS
  const savedHomePageVenues = JSON.parse(localStorage.getItem(key) || '{}')
  const savedHomePageVenueId = savedHomePageVenues[offererId]

  if (savedHomePageVenueId) {
    return savedHomePageVenueId
  }

  return
}
const setSavedPartnerPageVenueId = (
  context: Context,
  offererId: OffererId,
  venueId: string
): void => {
  if (!offererId || !storageAvailable('localStorage')) {
    return
  }

  const key =
    context === 'homepage'
      ? SAVED_HOME_PAGE_VENUE_ID_KEYS
      : SAVED_PARTNER_PAGE_VENUE_ID_KEYS
  const savedHomePageVenues = JSON.parse(localStorage.getItem(key) || '{}')
  savedHomePageVenues[offererId] = venueId
  localStorage.setItem(key, JSON.stringify(savedHomePageVenues))
}

export { getSavedPartnerPageVenueId, setSavedPartnerPageVenueId }
