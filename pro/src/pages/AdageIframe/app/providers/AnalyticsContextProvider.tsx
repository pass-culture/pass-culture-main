import React, { createContext, ReactNode, useState } from 'react'

type AnalyticsContextType = {
  hasClickedSearch: boolean
  setHasClickedSearch: (hasClickedSearch: boolean) => void
  filtersKeys: string[]
  setFiltersKeys: (filtersKeys: string[]) => void
}

const analyticsContextInitialValues: AnalyticsContextType = {
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
