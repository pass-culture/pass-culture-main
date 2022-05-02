import { CATEGORY_STATUS } from '.'

export type TSearchFilters = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  status: string
  creationMode: string
  periodBeginningDate: string
  periodEndingDate: string
}

export type Offerer = {
  id: string
  name: string
}

export type Venue = {
  name: string
  publicName?: string | null
  offererName: string
  isVirtual: boolean
  departementCode?: string | null
}

export type Stock = {
  beginningDatetime?: Date | null
  remainingQuantity: string | number
}

export type Offer = {
  id: string
  status: string
  isActive: boolean
  hasBookingLimitDatetimesPassed: boolean
  thumbUrl?: string | null
  isEducational: boolean
  name: string
  isEvent: boolean
  productIsbn?: string | null
  venue: Venue
  stocks: Stock[]
  isEditable: boolean
  isShowcase?: boolean | null
}

export type Option = {
  id: string
  displayName: string
}

export interface ICategorySubtypeItem {
  code: number
  label: string
  children: {
    code: number
    label: string
  }[]
}

export interface IOfferCategory {
  id: string
  proLabel: string
  isSelectable: boolean
}

export interface IOfferSubCategory {
  id: string
  categoryId: string
  proLabel: string
  isEvent: boolean
  conditionalFields: string[]
  canBeDuo: boolean
  canBeEducational: boolean
  onlineOfflinePlatform: CATEGORY_STATUS
  reimbursementRule: string
  isSelectable: boolean
}
