import { IOfferEducationalFormValues, ADRESS_TYPE } from './types'

export const INITIAL_EDUCATIONAL_FORM_VALUES: IOfferEducationalFormValues = {
  category: '',
  subCategory: '',
  title: '',
  description: '',
  duration: '',
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: ADRESS_TYPE.OFFERER_VENUE,
    otherAddress: '',
    venueId: '',
  },
  participants: [],
  accessibility: [],
  phone: '',
  email: '',
  notifications: false,
  notificationEmail: '',
}
