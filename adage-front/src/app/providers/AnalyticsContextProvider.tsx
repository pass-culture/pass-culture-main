import React, { createContext, ReactNode, useState } from 'react'

export type AnalyticsContextType = {
  hasClickedSearch: boolean
  setHasClickedSearch: (hasClickedSearch: boolean) => void
  filtersKeys: string[]
  setFiltersKeys: (filtersKeys: string[]) => void
}

export const analyticsContextInitialValues: AnalyticsContextType = {
  hasClickedSearch: false,
  setHasClickedSearch: () => null,
  filtersKeys: [],
  setFiltersKeys: () => null,
}

export const AnalyticsContext = createContext<AnalyticsContextType>(
  analyticsContextInitialValues
)

export const AnalyticsContextProvider = ({
  children,
}: {
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [hasClickedSearch, setHasClickedSearch] = useState<boolean>(false)
  const [filtersKeys, setFiltersKeys] = useState<string[]>([])

  // eslint-disable-next-line react/jsx-no-constructed-context-values
  const value = {
    hasClickedSearch,
    setHasClickedSearch,
    filtersKeys,
    setFiltersKeys,
  }

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  )
}
