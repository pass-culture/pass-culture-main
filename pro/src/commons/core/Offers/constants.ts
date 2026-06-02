import { DisplayableActivity, WithdrawalTypeEnum } from '@/apiClient/v1/new'
import type { SelectOption } from '@/commons/custom_types/form'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

import type { CollectiveSearchFiltersParams } from './types'

export enum CATEGORY_STATUS {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  // TODO (igabriele, 2025-07-30): Remove this once it's removed from the API.
  /** @deprecated `ONLINE_OR_OFFLINE` should never exist anymore in production. */
  ONLINE_OR_OFFLINE = 'ONLINE_OR_OFFLINE',
}

export enum OFFER_WIZARD_MODE {
  CREATION = 'creation',
  READ_ONLY = 'readonly',
  EDITION = 'edition',
}

export enum INDIVIDUAL_OFFER_WIZARD_STEP_IDS {
  DESCRIPTION = 'description',
  LOCATION = 'localisation',
  MEDIA = 'media',
  TARIFS = 'tarifs',
  TIMETABLE = 'horaires',
  PRACTICAL_INFOS = 'informations_pratiques',
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

const ALL_OFFERS = ''
const ALL_VENUES = 'all'
export const ALL_OFFERER_ADDRESSES = 'all'
export const ALL_FORMATS = 'all'
const ALL_EVENT_PERIODS = ''
export const DEFAULT_PAGE = 1
export const NUMBER_OF_OFFERS_PER_PAGE = 10
export const MAX_TOTAL_PAGES = 10
export const MAX_OFFERS_TO_DISPLAY = MAX_TOTAL_PAGES * NUMBER_OF_OFFERS_PER_PAGE

export const DEFAULT_SEARCH_FILTERS: IndividualOffersFilters = {
  nameOrIsbn: undefined,
  venueId: undefined,
  categoryId: undefined,
  status: undefined,
  creationMode: undefined,
  periodBeginningDate: undefined,
  periodEndingDate: undefined,
  page: DEFAULT_PAGE,
  offererAddressId: undefined,
}

export const DEFAULT_COLLECTIVE_SEARCH_FILTERS: CollectiveSearchFiltersParams =
  {
    name: ALL_OFFERS,
    offererId: 'all',
    venueId: ALL_VENUES,
    format: ALL_FORMATS,
    periodBeginningDate: ALL_EVENT_PERIODS,
    periodEndingDate: ALL_EVENT_PERIODS,
    page: DEFAULT_PAGE,
    status: [],
  }

export const ALL_OFFERER_ADDRESS_OPTION: SelectOption = {
  label: 'Toutes',
  value: ALL_OFFERER_ADDRESSES,
}

export const ALL_FORMATS_OPTION: SelectOption = {
  label: 'Tous',
  value: ALL_FORMATS,
}

export enum COLLECTIVE_OFFER_SUBTYPE {
  COLLECTIVE = 'COLLECTIVE',
  TEMPLATE = 'TEMPLATE',
}

export enum COLLECTIVE_OFFER_SUBTYPE_DUPLICATE {
  NEW_OFFER = 'NEW_OFFER',
  DUPLICATE = 'DUPLICATE',
}

export const CULTURAL_OUTREACH_ALLOWED_ACTIVITIES = new Set([
  DisplayableActivity.PRODUCTION_OR_PROMOTION_COMPANY,
  DisplayableActivity.ARTISTIC_COMPANY,
  DisplayableActivity.PERFORMANCE_HALL,
  DisplayableActivity.MUSEUM,
  DisplayableActivity.HERITAGE_SITE,
  DisplayableActivity.LIBRARY,
  DisplayableActivity.CULTURAL_MEDIATION,
])
