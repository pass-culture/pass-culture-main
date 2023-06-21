import React, { createContext, ReactNode, useMemo, useReducer } from 'react'

import { VenueResponse } from 'apiClient/adage'

import {
  filtersReducer,
  FiltersReducerAction,
} from '../components/OffersInstantSearch/OffersSearch/filtersReducer'
import { INITIAL_FILTERS } from '../constants'
import { Filters } from '../types'

type FiltersContextType = {
  currentFilters: Filters
  dispatchCurrentFilters: React.Dispatch<FiltersReducerAction>
}

const filtersContextInitialValues: FiltersContextType = {
  currentFilters: INITIAL_FILTERS,
  dispatchCurrentFilters: () => null,
}

export const FiltersContext = createContext<FiltersContextType>(
  filtersContextInitialValues
)

export const FiltersContextProvider = ({
  venueFilter,
  children,
}: {
  venueFilter?: VenueResponse | null
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [currentFilters, dispatchCurrentFilters] = useReducer(filtersReducer, {
    ...INITIAL_FILTERS,
    onlyInMyDpt: venueFilter ? false : INITIAL_FILTERS.onlyInMyDpt,
  })

  const value = useMemo(
    () => ({
      currentFilters,
      dispatchCurrentFilters,
    }),
    [currentFilters]
  )

  return (
    <FiltersContext.Provider value={value}>{children}</FiltersContext.Provider>
  )
}
