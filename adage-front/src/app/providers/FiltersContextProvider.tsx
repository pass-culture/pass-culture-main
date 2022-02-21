import React, {
  createContext,
  ReactNode,
  useMemo,
  useReducer,
  useState,
} from 'react'

import {
  filtersReducer,
  FiltersReducerAction,
} from 'app/components/OffersInstantSearch/OffersSearch/filtersReducer'
import {
  INITIAL_FACET_FILTERS,
  INITIAL_FILTERS,
  INITIAL_QUERY,
} from 'app/constants'
import { Facets, Filters } from 'app/types'

export const FiltersContext = createContext<{
  currentFilters: Filters
  dispatchCurrentFilters: React.Dispatch<FiltersReducerAction>
  query: string
  setQuery: (query: string) => void
  facetFilters: Facets
  setFacetFilters: (facets: Facets) => void
}>({
  currentFilters: INITIAL_FILTERS,
  dispatchCurrentFilters: () => null,
  query: INITIAL_QUERY,
  setQuery: () => null,
  facetFilters: INITIAL_FACET_FILTERS,
  setFacetFilters: () => null,
})

export const FiltersContextProvider = ({
  children,
}: {
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [currentFilters, dispatchCurrentFilters] = useReducer(
    filtersReducer,
    INITIAL_FILTERS
  )
  const [query, setQuery] = useState(INITIAL_QUERY)
  const [facetFilters, setFacetFilters] = useState<Facets>([
    ...INITIAL_FACET_FILTERS,
  ])

  const value = useMemo(
    () => ({
      currentFilters,
      dispatchCurrentFilters,
      query,
      setQuery,
      facetFilters,
      setFacetFilters,
    }),
    [currentFilters, query, facetFilters]
  )

  return (
    <FiltersContext.Provider value={value}>{children}</FiltersContext.Provider>
  )
}
