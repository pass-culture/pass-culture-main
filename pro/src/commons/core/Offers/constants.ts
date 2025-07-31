import { OfferStatus, WithdrawalTypeEnum } from 'apiClient/v1'
import { SelectOption } from 'commons/custom_types/form'

import {
  CollectiveOfferTypeEnum,
  CollectiveSearchFiltersParams,
  SearchFiltersParams,
} from './types'

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

export enum OFFER_WIZARD_MODE {
  CREATION = 'creation',
  READ_ONLY = 'readonly',
  EDITION = 'edition',
}

export enum INDIVIDUAL_OFFER_WIZARD_STEP_IDS {
  DETAILS = 'details',
  USEFUL_INFORMATIONS = 'pratiques',
  MEDIA = 'media',
  TARIFS = 'tarifs',
  STOCKS = 'stocks',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
  BOOKINGS = 'reservations',
}

export const OFFER_WITHDRAWAL_TYPE_LABELS = {
  [WithdrawalTypeEnum.ON_SITE]: 'Retrait sur place (guichet, comptoir...)',
  [WithdrawalTypeEnum.NO_TICKET]: 'Aucun billet n’est nécessaire',
  [WithdrawalTypeEnum.BY_EMAIL]: 'Les billets seront envoyés par email',
  [WithdrawalTypeEnum.IN_APP]: 'Les billets seront affichés dans l’application',
}

export const OFFER_STATUS_SOLD_OUT = OfferStatus.SOLD_OUT
export const OFFER_STATUS_PENDING = OfferStatus.PENDING
export const OFFER_STATUS_REJECTED = OfferStatus.REJECTED
export const OFFER_STATUS_DRAFT = OfferStatus.DRAFT

const ALL_OFFERS = ''
const ALL_VENUES = 'all'
export const ALL_OFFERER_ADDRESSES = 'all'
export const ALL_OFFERERS = 'all'
const ALL_CATEGORIES = 'all'
export const ALL_FORMATS = 'all'
export const ALL_STATUS = 'all'
export const ALL_CREATION_MODES = 'all'
const ALL_COLLECTIVE_OFFER_TYPE = 'all'
const ALL_EVENT_PERIODS = ''
export const DEFAULT_PAGE = 1
export const NUMBER_OF_OFFERS_PER_PAGE = 10
export const MAX_TOTAL_PAGES = 10
export const MAX_OFFERS_TO_DISPLAY = MAX_TOTAL_PAGES * NUMBER_OF_OFFERS_PER_PAGE
export const DEFAULT_SEARCH_FILTERS: SearchFiltersParams = {
  nameOrIsbn: ALL_OFFERS,
  offererId: 'all',
  venueId: ALL_VENUES,
  categoryId: ALL_CATEGORIES,
  format: ALL_FORMATS,
  status: ALL_STATUS,
  creationMode: ALL_CREATION_MODES,
  collectiveOfferType: ALL_COLLECTIVE_OFFER_TYPE,
  periodBeginningDate: ALL_EVENT_PERIODS,
  periodEndingDate: ALL_EVENT_PERIODS,
  page: DEFAULT_PAGE,
  offererAddressId: ALL_OFFERER_ADDRESSES,
}

export const DEFAULT_COLLECTIVE_SEARCH_FILTERS: CollectiveSearchFiltersParams =
  {
    nameOrIsbn: ALL_OFFERS,
    offererId: 'all',
    venueId: ALL_VENUES,
    format: ALL_FORMATS,
    collectiveOfferType: CollectiveOfferTypeEnum.ALL,
    periodBeginningDate: ALL_EVENT_PERIODS,
    periodEndingDate: ALL_EVENT_PERIODS,
    page: DEFAULT_PAGE,
    status: [],
  }

export const DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS: CollectiveSearchFiltersParams =
  {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    collectiveOfferType: CollectiveOfferTypeEnum.TEMPLATE,
  }

export const DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS: CollectiveSearchFiltersParams =
  {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    collectiveOfferType: CollectiveOfferTypeEnum.OFFER,
  }

export const ALL_VENUES_OPTION: SelectOption = {
  label: 'Tous les lieux',
  value: ALL_VENUES,
}

export const ALL_OFFERERS_OPTION: SelectOption = {
  label: 'Toutes les structures',
  value: ALL_OFFERERS,
}

export const ALL_OFFERER_ADDRESS_OPTION: SelectOption = {
  label: 'Toutes',
  value: ALL_OFFERER_ADDRESSES,
}

export const ALL_CATEGORIES_OPTION: SelectOption = {
  label: 'Toutes',
  value: ALL_CATEGORIES,
}

export const ALL_FORMATS_OPTION: SelectOption = {
  label: 'Tous',
  value: ALL_FORMATS,
}

export const CREATION_MODES_OPTIONS: SelectOption[] = [
  { label: 'Tous', value: ALL_CREATION_MODES },
  { label: 'Manuel', value: 'manual' },
  { label: 'Synchronisé', value: 'imported' },
]

export const COLLECTIVE_OFFER_TYPES_OPTIONS: SelectOption[] = [
  { label: 'Tout', value: ALL_COLLECTIVE_OFFER_TYPE },
  { label: 'Offre vitrine', value: 'template' },
  { label: 'Offre réservable', value: 'offer' },
]
