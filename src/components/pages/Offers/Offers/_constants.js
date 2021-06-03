export const OFFER_STATUS_ACTIVE = 'ACTIVE'
export const OFFER_STATUS_INACTIVE = 'INACTIVE'
export const OFFER_STATUS_SOLD_OUT = 'SOLD_OUT'
export const OFFER_STATUS_EXPIRED = 'EXPIRED'
export const OFFER_STATUS_PENDING = 'PENDING'
export const OFFER_STATUS_REJECTED = 'REJECTED'
export const OFFER_STATUS_DRAFT = 'DRAFT'
export const OFFER_STATUS_LIST = [
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_SOLD_OUT,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_DRAFT,
]

export const ALL_OFFERS = ''
export const ALL_VENUES = 'all'
export const ALL_OFFERERS = 'all'
export const ALL_TYPES = 'all'
export const ALL_STATUS = 'all'
export const ALL_CREATION_MODES = 'all'
export const ALL_EVENT_PERIODS = ''
export const DEFAULT_PAGE = 1
export const DEFAULT_SEARCH_FILTERS = {
  name: ALL_OFFERS,
  offererId: ALL_OFFERERS,
  venueId: ALL_VENUES,
  typeId: ALL_TYPES,
  status: ALL_STATUS,
  creationMode: ALL_CREATION_MODES,
  periodBeginningDate: ALL_EVENT_PERIODS,
  periodEndingDate: ALL_EVENT_PERIODS,
  page: DEFAULT_PAGE,
}

export const ALL_VENUES_OPTION = { displayName: 'Tous les lieux', id: ALL_VENUES }
export const ALL_TYPES_OPTION = { displayName: 'Toutes', id: ALL_TYPES }
const CREATION_MODES_OPTIONS = [
  { displayName: 'Tous les modes', id: ALL_CREATION_MODES },
  { displayName: 'Manuelle', id: 'manual' },
  { displayName: 'Importée', id: 'imported' },
]
export const [DEFAULT_CREATION_MODE, ...CREATION_MODES_FILTERS] = CREATION_MODES_OPTIONS
export const ADMINS_DISABLED_FILTERS_MESSAGE =
  'Sélectionnez une structure et/ou un lieu pour activer les filtres'
