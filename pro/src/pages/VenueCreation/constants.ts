import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { AccessiblityEnum } from 'core/shared'

import { VenueCreationFormValues } from './types'

export const DEFAULT_FORM_VALUES: VenueCreationFormValues = {
  ...DEFAULT_ADDRESS_FORM_VALUES,
  accessibility: {
    [AccessiblityEnum.VISUAL]: false,
    [AccessiblityEnum.MENTAL]: false,
    [AccessiblityEnum.AUDIO]: false,
    [AccessiblityEnum.MOTOR]: false,
    [AccessiblityEnum.NONE]: false,
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
