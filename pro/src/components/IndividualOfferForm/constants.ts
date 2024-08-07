import { ACCESSIBILITY_DEFAULT_VALUES } from './Accessibility/constants'
import { CATEGORIES_DEFAULT_VALUES } from './Categories/constants'
import { INFORMATIONS_DEFAULT_VALUES } from './Informations/constants'
import { NOTIFICATIONS_DEFAULT_VALUES } from './Notifications/constants'
import { OFFER_LOCATION_DEFAULT_VALUES } from './OfferLocation/constants'
import { USEFUL_INFORMATIONS_DEFAULT_VALUES } from './UsefulInformations/constants'

export const FORM_DEFAULT_VALUES_NO_OFFER_LOCATION = {
  ...INFORMATIONS_DEFAULT_VALUES,
  ...CATEGORIES_DEFAULT_VALUES,
  ...USEFUL_INFORMATIONS_DEFAULT_VALUES,
  ...ACCESSIBILITY_DEFAULT_VALUES,
  ...NOTIFICATIONS_DEFAULT_VALUES,
  isDuo: false,
}

export const FORM_DEFAULT_VALUES = {
  ...FORM_DEFAULT_VALUES_NO_OFFER_LOCATION,
  ...OFFER_LOCATION_DEFAULT_VALUES,
  isDuo: false,
}
