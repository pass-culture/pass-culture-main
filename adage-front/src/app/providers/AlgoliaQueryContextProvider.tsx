import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { INITIAL_QUERY } from 'app/constants'

export type AlgoliaQueryContextType = {
  query: string
  setQuery: (query: string) => void
}

export const alogliaQueryContextInitialValues: AlgoliaQueryContextType = {
  query: INITIAL_QUERY,
  setQuery: () => null,
}

export const AlgoliaQueryContext = createContext<AlgoliaQueryContextType>(
  alogliaQueryContextInitialValues
)

export const AlgoliaQueryContextProvider = ({
  children,
  values,
}: {
  children: ReactNode | ReactNode[]
  values?: AlgoliaQueryContextType
}): JSX.Element => {
  const [query, setQuery] = useState(values?.query || INITIAL_QUERY)

  const value = useMemo(
    () => ({
      query,
      setQuery,
    }),
    [query]
  )

  return (
    <AlgoliaQueryContext.Provider value={value}>
      {children}
    </AlgoliaQueryContext.Provider>
  )
}
