import React, { createContext, ReactNode, useMemo, useState } from 'react'

import { INITIAL_QUERY } from 'app/constants'

export type AlgoliaQueryContextType = {
  query: string
  setQuery: (query: string) => void
  queryTag: string
  setQueryTag: (queryTag: string) => void
  removeQuery: () => void
}

export const alogliaQueryContextInitialValues: AlgoliaQueryContextType = {
  query: INITIAL_QUERY,
  setQuery: () => null,
  queryTag: INITIAL_QUERY,
  setQueryTag: () => null,
  removeQuery: () => null,
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
  const [queryTag, setQueryTag] = useState(values?.queryTag || INITIAL_QUERY)

  const removeQuery = () => {
    setQuery(INITIAL_QUERY)
    setQueryTag(INITIAL_QUERY)
  }

  const value = useMemo(
    () => ({
      query,
      setQuery,
      queryTag,
      setQueryTag,
      removeQuery,
    }),
    [query, queryTag]
  )

  return (
    <AlgoliaQueryContext.Provider value={value}>
      {children}
    </AlgoliaQueryContext.Provider>
  )
}
