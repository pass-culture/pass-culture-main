import { IOfferEducationalFormValues } from './types'

export const INITIAL_EDUCATIONAL_FORM_VALUES: IOfferEducationalFormValues = {
  category: '',
  subCategory: '',
  title: '',
  description: '',
  duration: 0,
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: '',
    offererVenueId: '',
    otherAddress: '',
  },
  participants: [],
  accessibility: '',
  phone: '',
  email: '',
  notifications: false,
  notificationEmail: '',
}
