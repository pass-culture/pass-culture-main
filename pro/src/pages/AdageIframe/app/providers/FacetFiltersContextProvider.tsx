import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { getDefaultFacetFilterUAICodeValue } from 'pages/AdageIframe/utils/facetFilters'

import { Facets } from '../types'

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
  uai,
}: {
  children: ReactNode | ReactNode[]
  uai?: string | null
}): JSX.Element => {
  const [facetFilters, setFacetFilters] = useState<Facets>([
    getDefaultFacetFilterUAICodeValue(uai),
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
