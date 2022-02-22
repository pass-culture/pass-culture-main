import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { INITIAL_FACET_FILTERS } from 'app/constants'
import { Facets } from 'app/types'

export type FacetFiltersContextType = {
  facetFilters: Facets
  setFacetFilters: (facets: Facets) => void
}

export const facetFiltersContextInitialValues: FacetFiltersContextType = {
  facetFilters: INITIAL_FACET_FILTERS,
  setFacetFilters: () => null,
}

export const FacetFiltersContext = createContext<FacetFiltersContextType>(
  facetFiltersContextInitialValues
)

export const FacetFiltersContextProvider = ({
  children,
}: {
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [facetFilters, setFacetFilters] = useState<Facets>([
    ...INITIAL_FACET_FILTERS,
  ])

  const value = useMemo(
    () => ({
      facetFilters,
      setFacetFilters,
    }),
    [facetFilters]
  )

  return (
    <FacetFiltersContext.Provider value={value}>
      {children}
    </FacetFiltersContext.Provider>
  )
}
