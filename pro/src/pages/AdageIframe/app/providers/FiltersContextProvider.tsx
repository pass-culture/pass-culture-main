import React, { createContext, ReactNode, useMemo, useReducer } from 'react'

import { VenueResponse } from 'apiClient/adage'
import { Option, Filters } from 'pages/AdageIframe/app/types'

import {
  filtersReducer,
  FiltersReducerAction,
} from '../components/OffersInstantSearch/OffersSearch/filtersReducer'
import { INITIAL_FILTERS } from '../constants'

type FiltersContextType = {
  currentFilters: Filters
  dispatchCurrentFilters: React.Dispatch<FiltersReducerAction>
}

const filtersContextInitialValues: FiltersContextType = {
  currentFilters: INITIAL_FILTERS,
  dispatchCurrentFilters: () => null,
}

const FiltersContext = createContext<FiltersContextType>(
  filtersContextInitialValues
)

export const FiltersContextProvider = ({
  venueFilter,
  domainFilter,
  children,
}: {
  venueFilter?: VenueResponse | null
  domainFilter?: Option<number> | null
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [currentFilters, dispatchCurrentFilters] = useReducer(filtersReducer, {
    ...INITIAL_FILTERS,
    onlyInMyDpt: venueFilter ? false : INITIAL_FILTERS.onlyInMyDpt,
    domains: domainFilter ? [domainFilter] : [],
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
