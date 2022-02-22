import React, { createContext, ReactNode, useMemo, useReducer } from 'react'

import {
  filtersReducer,
  FiltersReducerAction,
} from 'app/components/OffersInstantSearch/OffersSearch/filtersReducer'
import { INITIAL_FILTERS } from 'app/constants'
import { Filters } from 'app/types'

export type FiltersContextType = {
  currentFilters: Filters
  dispatchCurrentFilters: React.Dispatch<FiltersReducerAction>
}

export const filtersContextInitialValues: FiltersContextType = {
  currentFilters: INITIAL_FILTERS,
  dispatchCurrentFilters: () => null,
}

export const FiltersContext = createContext<FiltersContextType>(
  filtersContextInitialValues
)

export const FiltersContextProvider = ({
  children,
}: {
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [currentFilters, dispatchCurrentFilters] = useReducer(
    filtersReducer,
    INITIAL_FILTERS
  )

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
