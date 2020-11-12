export const OFFER_STATUS_ACTIVE = 'active'
export const OFFER_STATUS_INACTIVE = 'inactive'
export const OFFER_STATUS_SOLDOUT = 'soldOut'
export const OFFER_STATUS_EXPIRED = 'expired'
export const OFFER_STATUS_LIST = [
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_SOLDOUT,
  OFFER_STATUS_EXPIRED,
]

export const ALL_OFFERS = ''
export const ALL_VENUES = 'all'
export const ALL_OFFERERS = 'all'
export const ALL_TYPES = 'all'
export const ALL_STATUS = 'all'
export const ALL_CREATION_MODES = 'all'
export const DEFAULT_SEARCH_FILTERS = {
  name: ALL_OFFERS,
  offererId: ALL_OFFERERS,
  venueId: ALL_VENUES,
  typeId: ALL_TYPES,
  status: ALL_STATUS,
  creationMode: ALL_CREATION_MODES,
}
export const DEFAULT_PAGE = 1

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
