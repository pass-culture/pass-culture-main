import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import { VenueResponse } from 'apiClient/adage'
import { ADAGE_FILTERS_DEFAULT_VALUES } from 'pages/AdageIframe/app/components/OffersInstantSearch/utils'

interface SearchFormValuesWithQuery {
  domains: number[]
  students: string[]
  departments: string[]
  academies: string[]
  eventAddressType: string
  geolocRadius: number
  formats: string[]
  venue: VenueResponse | null
}

interface AdageFilterState {
  adageFilter: SearchFormValuesWithQuery
  adageQuery: string | null
}

const initialState: AdageFilterState = {
  adageFilter: {
    ...ADAGE_FILTERS_DEFAULT_VALUES,
  },
  adageQuery: null,
}

const adageFilterSlice = createSlice({
  name: 'adageFilter',
  initialState,
  reducers: {
    setAdageFilter(state, action: PayloadAction<SearchFormValuesWithQuery>) {
      state.adageFilter = action.payload
    },
    setAdageQuery(state, action: PayloadAction<string>) {
      state.adageQuery = action.payload
    },
  },
})

export const { setAdageFilter, setAdageQuery } = adageFilterSlice.actions

export const adageFilterReducer = adageFilterSlice.reducer
