import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { AccessibilityEnum } from 'core/shared/types'

import { VenueCreationFormValues } from './types'

export const DEFAULT_INTITIAL_OPENING_HOURS = {
  morningStartingHour: '',
  morningEndingHour: '',
  afternoonStartingHour: '',
  afternoonEndingHour: '',
  isAfternoonOpen: false,
}

export const DEFAULT_FORM_VALUES: VenueCreationFormValues = {
  ...DEFAULT_ADDRESS_FORM_VALUES,
  accessibility: {
    [AccessibilityEnum.VISUAL]: false,
    [AccessibilityEnum.MENTAL]: false,
    [AccessibilityEnum.AUDIO]: false,
    [AccessibilityEnum.MOTOR]: false,
    [AccessibilityEnum.NONE]: false,
  },
  bannerMeta: undefined,
  bannerUrl: '',
  bookingEmail: '',
  comment: '',
  name: '',
  publicName: '',
  siret: '',
  venueType: '',
}
