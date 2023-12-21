import React, {
  createContext,
  Dispatch,
  ReactNode,
  SetStateAction,
  useMemo,
  useState,
} from 'react'

import { VenueResponse } from 'apiClient/adage'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

import { Facets } from '../types'

type FacetFiltersContextType = {
  facetFilters: Facets
  setFacetFilters: Dispatch<SetStateAction<Facets>>
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
  venueFilter,
  domainFilter,
}: {
  children: ReactNode | ReactNode[]
  uai?: string | null
  venueFilter?: VenueResponse | null
  domainFilter?: number | null
}): JSX.Element => {
  const [facetFilters, setFacetFilters] = useState<Facets>([
    ...getDefaultFacetFilterUAICodeValue(uai, venueFilter, domainFilter),
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
