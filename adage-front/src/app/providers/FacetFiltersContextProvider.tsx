import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { LEGACY_INITIAL_FACET_FILTERS } from 'app/constants'
import { Facets } from 'app/types'

export type FacetFiltersContextType = {
  facetFilters: Facets
  setFacetFilters: (facets: Facets) => void
}

export const facetFiltersContextInitialValues: FacetFiltersContextType = {
  facetFilters: LEGACY_INITIAL_FACET_FILTERS,
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
    ...LEGACY_INITIAL_FACET_FILTERS,
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
