export type SearchFilters = {
  nameOrIsbn?: string
  offererId?: number | string
  venueId?: number | string
  categoryId?: string | string
  status?: string
  creationMode?: string
  periodBeginningDate?: string
  periodEndingDate?: string
}

export type SearchFiltersAPI = {
  nameOrIsbn?: string
  offererId?: number
  venueId?: number
  categoryId?: string
  status?: string
  creationMode?: string
  periodBeginningDate?: string
  periodEndingDate?: string
}

export type Offerer = {
  id: string
  name: string
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
  venue: {
    name: string
    publicName?: string | null
    offererName: string
    isVirtual: boolean
    departementCode?: string | null
  }
  stocks: {
    beginningDatetime?: Date | null
    remainingQuantity: string | number
  }[]
  isEditable: boolean
  isShowcase?: boolean | null
}
