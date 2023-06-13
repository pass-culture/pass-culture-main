import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { VenueResponse } from 'apiClient/adage'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

import { computeVenueFacetFilter } from '../components/OffersInstantSearch/utils'
import { Facets } from '../types'

type FacetFiltersContextType = {
  facetFilters: Facets
  setFacetFilters: (facets: Facets) => void
}

const facetFiltersContextInitialValues: FacetFiltersContextType = {
  facetFilters: [],
  setFacetFilters: () => null,
}

export const FacetFiltersContext = createContext<FacetFiltersContextType>(
  facetFiltersContextInitialValues
)

export const FacetFiltersContextProvider = ({
  children,
  uai,
  departmentCode,
  venueFilter,
}: {
  children: ReactNode | ReactNode[]
  uai?: string | null
  departmentCode?: string | null
  venueFilter?: VenueResponse | null
}): JSX.Element => {
  const defaultFacetFilters = venueFilter
    ? [
        computeVenueFacetFilter(venueFilter),
        ...getDefaultFacetFilterUAICodeValue(uai, departmentCode, venueFilter),
      ]
    : [...getDefaultFacetFilterUAICodeValue(uai, departmentCode, venueFilter)]
  const [facetFilters, setFacetFilters] = useState<Facets>(defaultFacetFilters)

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
