const TEXT_INPUT_DEFAULT_VALUE = ''
const SELECT_DEFAULT_VALUE = ''

export const DEFAULT_FORM_VALUES = {
  author: TEXT_INPUT_DEFAULT_VALUE,
  bookingEmail: TEXT_INPUT_DEFAULT_VALUE,
  description: TEXT_INPUT_DEFAULT_VALUE,
  durationMinutes: null,
  isbn: TEXT_INPUT_DEFAULT_VALUE,
  isDuo: true,
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
  type: SELECT_DEFAULT_VALUE,
  url: TEXT_INPUT_DEFAULT_VALUE,
  venueId: SELECT_DEFAULT_VALUE,
  visa: TEXT_INPUT_DEFAULT_VALUE,
  withdrawalDetails: TEXT_INPUT_DEFAULT_VALUE,
}

export const BASE_OFFER_FIELDS = ['description', 'name', 'type', 'venueId', 'withdrawalDetails']
export const EDITED_OFFER_READ_ONLY_FIELDS = [
  'type',
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
export const MANDATORY_FIELDS = ['name', 'venueId', 'offererId', 'url', 'bookingEmail']
