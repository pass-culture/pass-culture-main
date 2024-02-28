import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { AccessiblityEnum } from 'core/shared'

import { VenueFormValues } from './types'

export const DEFAULT_FORM_VALUES: VenueFormValues = {
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
  departmentCode: '',
  description: '',
  email: '',
  id: undefined,
  isAccessibilityAppliedOnAllOffers: false,
  isPermanent: false,
  isVenueVirtual: false,
  isWithdrawalAppliedOnAllOffers: false,
  name: '',
  phoneNumber: '',
  publicName: '',
  reimbursementPointId: null,
  siret: '',
  venueLabel: '',
  venueSiret: null,
  venueType: '',
  webSite: '',
  withdrawalDetails: '',
}
