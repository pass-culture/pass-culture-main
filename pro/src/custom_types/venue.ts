import { Offerer } from './offerer'

export type VenueListItem = {
  id: string
  managingOffererId: string
  name: string
  offererName: string
  publicName: string
  isVirtual: boolean
  bookingEmail: string | null
  withdrawalDetails: string | null
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  businessUnitId: number | null
  businessUnit?: BusinessUnitResponseModel
  siret: string | null
  isBusinessUnitMainVenue: boolean | null
}

type BusinessUnitResponseModel = {
  id: number
  iban?: string
  bic?: string
  name: string
  siret?: string
}

enum VenueType {
  'VISUAL_ARTS' = 'Arts visuels, arts plastiques et galeries',
  'CULTURAL_CENTRE' = 'Centre culturel',
  'ARTISTIC_COURSE' = 'Cours et pratique artistiques',
  'SCIENTIFIC_CULTURE' = 'Culture scientifique',
  'FESTIVAL' = 'Festival',
  'GAMES' = 'Jeux / Jeux vidéos',
  'BOOKSTORE' = 'Librairie',
  'LIBRARY' = 'Bibliothèque ou médiathèque',
  'MUSEUM' = 'Musée',
  'RECORD_STORE' = 'Musique - Disquaire',
  'MUSICAL_INSTRUMENT_STORE' = 'Musique - Magasin d’instruments',
  'CONCERT_HALL' = 'Musique - Salle de concerts',
  'DIGITAL' = 'Offre numérique',
  'PATRIMONY_TOURISM' = 'Patrimoine et tourisme',
  'MOVIE' = 'Cinéma - Salle de projections',
  'PERFORMING_ARTS' = 'Spectacle vivant',
  'CREATIVE_ARTS_STORE' = 'Magasin arts créatifs',
  'ADMINISTRATIVE' = 'Lieu administratif',
  'OTHER' = 'Autre',
}

export type Venue = {
  address?: string
  bic?: string
  bookingEmail?: string
  city?: string
  comment?: string
  dateCreated: Date
  dateModifiedAtLastProvider?: Date
  demarchesSimplifieesApplicationId?: string
  departementCode?: string
  fieldsUpdated: string[]
  iban?: string
  id: string
  idAtProviders?: string
  isBusinessUnitMainVenue?: boolean
  isPermanent?: boolean
  isValidated: boolean
  isVirtual: boolean
  lastProviderId?: string
  latitude?: number
  longitude?: number
  managingOfferer: Offerer
  managingOffererId: string
  name: string
  postalCode?: string
  publicName?: string
  siret?: string
  venueLabelId?: string
  venueTypeCode?: VenueType
  withdrawalDetails?: string
  description?: string
  audioDisabilityCompliant?: boolean
  mentalDisabilityCompliant?: boolean
  motorDisabilityCompliant?: boolean
  visualDisabilityCompliant?: boolean
  contact?: {
    email?: string
    website?: string
    phone_number?: string
    social_medias?: Record<
      'facebook' | 'instagram' | 'snapchat' | 'twitter',
      string
    >
  }
  businessUnitId?: number
  businessUnit?: BusinessUnitResponseModel
  bannerUrl?: string
  bannerMeta?: {
    file_name: string
    content_type: string
  }
}

export type VenueStats = {
  activeBookingsQuantity: number
  validatedBookingsQuantity: number
  activeOffersCount: number
  soldOutOffersCount: number
}
