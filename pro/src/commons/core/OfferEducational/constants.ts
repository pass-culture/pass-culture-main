import { CollectiveLocationType, OfferAddressType } from 'apiClient/v1'
import { VisibilityFormValues } from 'pages/CollectiveOfferVisibility/components/CollectiveOfferVisibility/CollectiveOfferVisibility'

import {
  OfferEducationalFormValues,
  OfferEducationalStockFormValues,
} from './types'
import { buildStudentLevelsMapWithDefaultValue } from './utils/buildStudentLevelsMapWithDefaultValue'

export function getDefaultEducationalValues(
  isMarseilleEnabled?: boolean
): OfferEducationalFormValues {
  return {
    title: '',
    description: '',
    duration: '',
    offererId: '',
    venueId: '',
    eventAddress: {
      addressType: OfferAddressType.OFFERER_VENUE,
      otherAddress: '',
      venueId: 0,
    },
    location: {
      locationType: CollectiveLocationType.ADDRESS,
      address: {
        label: '',
        id_oa: '',
        isManualEdition: false,
        isVenueAddress: false,
      },
    },
    latitude: '',
    longitude: '',
    city: '',
    postalCode: '',
    street: '',
    banId: '',
    coords: '',
    'search-addressAutocomplete': '',
    addressAutocomplete: '',
    interventionArea: [],
    participants: buildStudentLevelsMapWithDefaultValue(
      false,
      isMarseilleEnabled
    ),
    accessibility: {
      visual: false,
      audio: false,
      motor: false,
      mental: false,
      none: false,
    },
    notificationEmails: [{ email: '' }],
    domains: [],
    'search-domains': '',
    'search-formats': '',
    'search-interventionArea': '',
    priceDetail: '',
    imageUrl: '',
    imageCredit: '',
    nationalProgramId: '',
    isTemplate: false,
    datesType: 'permanent',
    beginningDate: '',
    endingDate: '',
    hour: '',
    formats: [],
    contactOptions: {
      phone: false,
      email: false,
      form: false,
    },
    contactFormType: 'form',
  }
}

export const DEFAULT_EAC_STOCK_FORM_VALUES: OfferEducationalStockFormValues = {
  startDatetime: '',
  endDatetime: '',
  eventTime: '',
  numberOfPlaces: null,
  totalPrice: null,
  bookingLimitDatetime: '',
  priceDetail: '',
}

export const DEFAULT_VISIBILITY_FORM_VALUES: VisibilityFormValues = {
  visibility: 'one',
  institution: '',
  teacher: undefined,
}

export const MAX_DESCRIPTION_LENGTH = 1500

export const MAX_PRICE_DETAILS_LENGTH = 1000

export const modelTemplate = `**Thèmes et mots clefs de la proposition d’éducation artistique et culturelle :**\nQuels sujets et grandes notions sont abordés ?\n\n**Déroulé de l’action :**\nComment se compose la proposition ?\nQuelles connaissances les élèves acquièrent-ils ?\nDe quelles pratiques font-ils l’expérience ?\nQuelles démarches artistiques ou scientifiques découvrent-ils ?\n\n**Les intervenants des arts ou des sciences :**\nQui les élèves vont-ils rencontrer ?\nQuelles sont les qualifications des intervenants ?`
