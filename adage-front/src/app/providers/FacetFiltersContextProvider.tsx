import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { LEGACY_INITIAL_FACET_FILTERS } from 'app/constants'
import { useActiveFeature } from 'app/hooks/useActiveFeature'
import { Facets } from 'app/types'

export type FacetFiltersContextType = {
  facetFilters: Facets
  setFacetFilters: (facets: Facets) => void
}

export const facetFiltersContextInitialValues: FacetFiltersContextType = {
  facetFilters: [],
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
  const useNewAlgoliaIndex = useActiveFeature(
    'ENABLE_NEW_ALGOLIA_INDEX_ON_ADAGE'
  )

  const [facetFilters, setFacetFilters] = useState<Facets>(
    useNewAlgoliaIndex ? [] : [...LEGACY_INITIAL_FACET_FILTERS]
  )

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
