import { AccessibilityEnum } from '@/commons/core/shared/types'

export const SUBCATEGORIES_FIELDS_DEFAULT_VALUES = {
  gtl_id: '',
  musicType: '',
  musicSubType: '',
  showType: '',
  showSubType: '',
  author: '',
  ean: '',
  performer: '',
  speaker: '',
  stageDirector: '',
  visa: '',
  durationMinutes: '',
  withdrawalType: undefined,
  withdrawalDelay: undefined,
}

const OFFER_LOCATION_DEFAULT_VALUES = {
  offerLocation: '',
  locationLabel: '',
  manuallySetAddress: false,
  street: '',
  'search-addressAutocomplete': '',
  addressAutocomplete: '',
  postalCode: '',
  city: '',
  coords: '',
  latitude: '',
  longitude: '',
  banId: '',
}

const INFORMATIONS_DEFAULT_VALUES = {
  name: '',
  description: '',
  author: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['author'],
  ean: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['ean'],
  performer: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['performer'],
  speaker: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['speaker'],
  stageDirector: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['stageDirector'],
  visa: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['visa'],
  durationMinutes: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['durationMinutes'],
}

const CATEGORIES_DEFAULT_VALUES = {
  subCategoryFields: [],
  categoryId: '',
  subcategoryId: '',
  isEvent: false,
  ...SUBCATEGORIES_FIELDS_DEFAULT_VALUES,
}

const USEFUL_INFORMATIONS_DEFAULT_VALUES = {
  offererId: '',
  venueId: '',
  withdrawalDetails: '',
  withdrawalType: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['withdrawalType'],
  withdrawalDelay: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['withdrawalDelay'],
  isNational: false,
  url: '',
  bookingContact: '',
}

const ACCESSIBILITY_DEFAULT_VALUES = {
  accessibility: {
    [AccessibilityEnum.VISUAL]: false,
    [AccessibilityEnum.MENTAL]: false,
    [AccessibilityEnum.AUDIO]: false,
    [AccessibilityEnum.MOTOR]: false,
    [AccessibilityEnum.NONE]: false,
  },
}

const NOTIFICATIONS_DEFAULT_VALUES = {
  receiveNotificationEmails: false,
  bookingEmail: '',
}

export const FORM_DEFAULT_VALUES = {
  ...INFORMATIONS_DEFAULT_VALUES,
  ...CATEGORIES_DEFAULT_VALUES,
  ...USEFUL_INFORMATIONS_DEFAULT_VALUES,
  ...ACCESSIBILITY_DEFAULT_VALUES,
  ...NOTIFICATIONS_DEFAULT_VALUES,
  ...OFFER_LOCATION_DEFAULT_VALUES,
  isDuo: false,
}

export enum OFFER_LOCATION {
  OTHER_ADDRESS = 'other',
}
