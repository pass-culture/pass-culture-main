export const ALL_OFFERS = ''
export const ALL_VENUES = 'all'
export const ALL_OFFERERS = 'all'
export const ALL_TYPES = 'all'
export const ALL_STATUS = 'all'
const ALL_CREATION_MODES = 'all'
export const DEFAULT_PAGE = 1
export const ALL_VENUES_OPTION = { displayName: 'Tous les lieux', id: ALL_VENUES }
export const ALL_TYPES_OPTION = { displayName: 'Toutes', id: ALL_TYPES }
const CREATION_MODES_OPTIONS = [
  { displayName: 'Tous les modes', id: ALL_CREATION_MODES },
  { displayName: 'Manuelle', id: 'manual' },
  { displayName: 'Importée', id: 'imported' },
]
export const [DEFAULT_CREATION_MODE, ...CREATION_MODES_FILTERS] = CREATION_MODES_OPTIONS
