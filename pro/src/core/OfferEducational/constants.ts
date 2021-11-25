import { IOfferEducationalFormValues, ADRESS_TYPE } from './types'

export const INITIAL_EDUCATIONAL_FORM_VALUES: IOfferEducationalFormValues = {
  category: '',
  subCategory: '',
  title: '',
  description: '',
  duration: 0,
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: ADRESS_TYPE.OFFERER_VENUE,
    otherAddress: '',
    venueId: '',
  },
  participants: [],
  visualDisabilityCompliant: false,
  mentalDisabilityCompliant: false,
  motorDisabilityCompliant: false,
  audioDisabilityCompliant: false,
  phone: '',
  email: '',
  notifications: false,
  notificationEmail: '',
}
