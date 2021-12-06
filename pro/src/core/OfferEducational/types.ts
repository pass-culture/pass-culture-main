export type IUserVenue = {
  id: string
  name: string
  address: {
    street: string
    city: string
    postalCode: string
  }
}

export type IUserOfferer = {
  id: string
  name: string
  managedVenues: IUserVenue[]
}

export enum ADRESS_TYPE {
  OFFERER_VENUE = 'offererVenue',
  SCHOOL = 'school',
  OTHER = 'other',
}

export enum ACCESSIBILITY {
  VISUAL = 'visual',
  MENTAL = 'mental',
  AUDIO = 'audio',
  MOTOR = 'motor',
  NONE = 'none',
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
  duration: string
  offererId: string
  venueId: string
  eventAddress: {
    addressType: ADRESS_TYPE
    otherAddress: string
    venueId: string
  }
  participants: {
    quatrieme: boolean
    troisieme: boolean
    CAPAnnee1: boolean
    CAPAnnee2: boolean
    seconde: boolean
    premiere: boolean
    terminale: boolean
    all: boolean
  }
  accessibility: {
    visual: boolean
    audio: boolean
    motor: boolean
    mental: boolean
    none: boolean
  }
  phone: string
  email: string
  notifications: boolean
  notificationEmail: string
}

export type GetIsOffererEligibleToEducationalOffer = Adapter<
  string,
  { isOffererEligibleToEducationalOffer: boolean }
>
