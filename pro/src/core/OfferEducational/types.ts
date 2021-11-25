export type IUserVenue = {
  id: string
  name: string
}

export type IUserOfferer = {
  id: string
  name: string
  siren: string
  managedVenues: IUserVenue[]
}

export type IEducationalCategory = {
  id: string
  label: string
}

export type IEducationalSubCategory = {
  id: string
  categoryId: string
  label: string
}

export type IOfferEducationalFormValues = {
  category: string
  subCategory: string
  title: string
  description: string
  duration: number
  offererId: string
  venueId: string
  eventAddress: {
    addressType: 'school' | 'offererVenue' | 'other' | ''
    offererVenueId: string
    otherAddress: string
  }
  participants: string[]
  accessibility: string
  phone: string
  email: string
  notifications: boolean
  notificationEmail: string
}
