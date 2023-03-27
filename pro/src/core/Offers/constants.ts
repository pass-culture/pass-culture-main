import { OfferStatus } from 'apiClient/v1'

import { TSearchFilters } from './types'

export enum OFFER_TYPES {
  INDIVIDUAL_OR_DUO = 'INDIVIDUAL_OR_DUO',
  EDUCATIONAL = 'EDUCATIONAL',
}

export enum INDIVIDUAL_OFFER_SUBTYPE {
  PHYSICAL_GOOD = 'PHYSICAL_GOOD',
  VIRTUAL_GOOD = 'VIRTUAL_GOOD',
  PHYSICAL_EVENT = 'PHYSICAL_EVENT',
  VIRTUAL_EVENT = 'VIRTUAL_EVENT',
}

export enum COLLECTIVE_OFFER_SUBTYPE {
  COLLECTIVE = 'COLLECTIVE',
  TEMPLATE = 'TEMPLATE',
}

export enum COLLECTIVE_OFFER_SUBTYPE_DUPLICATE {
  NEW_OFFER = 'NEW_OFFER',
  DUPLICATE = 'DUPLICATE',
}

export enum CATEGORY_STATUS {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  ONLINE_OR_OFFLINE = 'ONLINE_OR_OFFLINE',
}

export enum OFFER_WITHDRAWAL_TYPE_OPTIONS {
  ON_SITE = 'on_site',
  NO_TICKET = 'no_ticket',
  BY_EMAIL = 'by_email',
}

export enum OFFER_WIZARD_MODE {
  CREATION = 'creation',
  DRAFT = 'draft',
  EDITION = 'edition',
}

export const OFFER_WITHDRAWAL_TYPE_LABELS = {
  [OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE]:
    'Retrait sur place (guichet, comptoir...)',
  [OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET]: 'Évènement sans billet',
  [OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL]: 'Envoi par e-mail',
}

export const OFFER_STATUS_ACTIVE = OfferStatus.ACTIVE
export const OFFER_STATUS_INACTIVE = OfferStatus.INACTIVE
export const OFFER_STATUS_SOLD_OUT = OfferStatus.SOLD_OUT
export const OFFER_STATUS_EXPIRED = OfferStatus.EXPIRED
export const OFFER_STATUS_PENDING = OfferStatus.PENDING
export const OFFER_STATUS_REJECTED = OfferStatus.REJECTED
export const OFFER_STATUS_DRAFT = OfferStatus.DRAFT
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
export const ALL_CATEGORIES = 'all'
export const ALL_STATUS = 'all'
export const ALL_CREATION_MODES = 'all'
export const ALL_COLLECTIVE_OFFER_TYPE = 'all'
export const ALL_EVENT_PERIODS = ''
export const DEFAULT_PAGE = 1
export const NUMBER_OF_OFFERS_PER_PAGE = 10
export const MAX_TOTAL_PAGES = 50
export const MAX_OFFERS_TO_DISPLAY = MAX_TOTAL_PAGES * NUMBER_OF_OFFERS_PER_PAGE
export const DEFAULT_AUDIENCE = 'individual'
export const DEFAULT_SEARCH_FILTERS: TSearchFilters = {
  nameOrIsbn: ALL_OFFERS,
  offererId: 'all',
  venueId: ALL_VENUES,
  categoryId: ALL_CATEGORIES,
  status: ALL_STATUS,
  creationMode: ALL_CREATION_MODES,
  collectiveOfferType: ALL_COLLECTIVE_OFFER_TYPE,
  periodBeginningDate: ALL_EVENT_PERIODS,
  periodEndingDate: ALL_EVENT_PERIODS,
}

export const ALL_VENUES_OPTION = {
  displayName: 'Tous les lieux',
  id: ALL_VENUES,
}
export const ALL_CATEGORIES_OPTION = {
  displayName: 'Toutes',
  id: ALL_CATEGORIES,
}
const CREATION_MODES_OPTIONS = [
  { displayName: 'Tous', id: ALL_CREATION_MODES },
  { displayName: 'Manuel', id: 'manual' },
  { displayName: 'Synchronisé', id: 'imported' },
]
const COLLECTIVE_OFFER_TYPES_OPTIONS = [
  { displayName: 'Tout', id: ALL_CREATION_MODES },
  { displayName: 'Offre vitrine', id: 'template' },
  { displayName: 'Offre réservable', id: 'offer' },
]

export const [DEFAULT_CREATION_MODE, ...CREATION_MODES_FILTERS] =
  CREATION_MODES_OPTIONS

export const [
  DEFAULT_COLLECTIVE_OFFER_TYPE,
  ...COLLECTIVE_OFFER_TYPES_FILTERS
] = COLLECTIVE_OFFER_TYPES_OPTIONS
export const ADMINS_DISABLED_FILTERS_MESSAGE =
  'Sélectionnez une structure et/ou un lieu pour activer les filtres'

export const LIVRE_PAPIER_SUBCATEGORY_ID = 'LIVRE_PAPIER'

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

export const SYNCHRONIZED_OFFER_EDITABLE_FIELDS = {
  ALL_PROVIDERS: [
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
    'externalTicketOfficeUrl',
    'accessibility',
  ],
  ALLOCINE: ['isDuo'],
}

export const EDITED_OFFER_READ_ONLY_FIELDS = [
  'categoryId',
  'subcategoryId',
  'offererId',
  'venueId',
]
