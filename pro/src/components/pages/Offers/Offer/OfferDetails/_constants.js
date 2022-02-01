/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

export const TEXT_INPUT_DEFAULT_VALUE = ''
const SELECT_DEFAULT_VALUE = ''

export const DEFAULT_FORM_VALUES = {
  author: TEXT_INPUT_DEFAULT_VALUE,
  bookingEmail: TEXT_INPUT_DEFAULT_VALUE,
  description: TEXT_INPUT_DEFAULT_VALUE,
  durationMinutes: null,
  isbn: TEXT_INPUT_DEFAULT_VALUE,
  isDuo: true,
  isEducational: false,
  noDisabilityCompliant: false,
  audioDisabilityCompliant: false,
  mentalDisabilityCompliant: false,
  motorDisabilityCompliant: false,
  visualDisabilityCompliant: false,
  isNational: false,
  name: TEXT_INPUT_DEFAULT_VALUE,
  musicSubType: SELECT_DEFAULT_VALUE,
  musicType: SELECT_DEFAULT_VALUE,
  offererId: SELECT_DEFAULT_VALUE,
  performer: TEXT_INPUT_DEFAULT_VALUE,
  showSubType: SELECT_DEFAULT_VALUE,
  showType: SELECT_DEFAULT_VALUE,
  stageDirector: TEXT_INPUT_DEFAULT_VALUE,
  speaker: TEXT_INPUT_DEFAULT_VALUE,
  categoryId: SELECT_DEFAULT_VALUE,
  subcategoryId: SELECT_DEFAULT_VALUE,
  url: TEXT_INPUT_DEFAULT_VALUE,
  externalTicketOfficeUrl: TEXT_INPUT_DEFAULT_VALUE,
  venueId: SELECT_DEFAULT_VALUE,
  visa: TEXT_INPUT_DEFAULT_VALUE,
  // set to null to set default value from venue
  withdrawalDetails: null,
}

export const BASE_OFFER_FIELDS = [
  'description',
  'audioDisabilityCompliant',
  'mentalDisabilityCompliant',
  'motorDisabilityCompliant',
  'visualDisabilityCompliant',
  'name',
  'externalTicketOfficeUrl',
  'subcategoryId',
  'categoryId',
  'venueId',
  'withdrawalDetails',
]
export const EDITED_OFFER_READ_ONLY_FIELDS = [
  'categoryId',
  'subcategoryId',
  'musicType',
  'musicSubType',
  'offererId',
  'showType',
  'showSubType',
  'venueId',
]
export const EXTRA_DATA_FIELDS = [
  'author',
  'isbn',
  'musicType',
  'musicSubType',
  'performer',
  'showType',
  'showSubType',
  'speaker',
  'stageDirector',
  'visa',
]
export const MANDATORY_FIELDS = [
  'name',
  'venueId',
  'offererId',
  'url',
  'bookingEmail',
  'categoryId',
  'subcategoryId',
]

export const SYNCHRONIZED_OFFER_EDITABLE_FIELDS = {
  ALL_PROVIDERS: [
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
    'externalTicketOfficeUrl',
  ],
  ALLOCINE: ['isDuo'],
}

export const PLATFORM = {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  ONLINE_OR_OFFLINE: 'ONLINE_OR_OFFLINE',
}

export const NOT_REIMBURSED = 'NOT_REIMBURSED'

export const OFFER_OPTIONS = {
  DUO: 'DUO',
  EDUCATIONAL: 'EDUCATIONAL',
  NONE: 'NONE',
}

export const CAN_CREATE_FROM_ISBN_SUBCATEGORIES = ['LIVRE_PAPIER']
