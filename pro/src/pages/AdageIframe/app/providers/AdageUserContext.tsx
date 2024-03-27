import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useState,
} from 'react'

import { AuthenticatedResponse } from 'apiClient/adage'

import { SearchFormValues } from '../components/OffersInstantSearch/OffersSearch/OffersSearch'

type AdageUserContextType = {
  adageUser: AuthenticatedResponse | null
  favoritesCount?: number
  setFavoriteCount?: Dispatch<SetStateAction<number>>
  filters: { filters: SearchFormValues | null; query: string }
  setFilters?: Dispatch<
    SetStateAction<{ filters: SearchFormValues | null; query: string }>
  >
}

export const AdageUserContext = createContext<AdageUserContextType>({
  adageUser: null,
  filters: {
    filters: null,
    query: '',
  },
})

export const AdageUserContextProvider = ({
  children,
  adageUser,
}: {
  children: ReactNode
  adageUser: AdageUserContextType['adageUser']
}): JSX.Element => {
  const [favoritesCount, setFavoriteCount] = useState<number>(0)
  const [filters, setFilters] = useState<{
    filters: SearchFormValues | null
    query: string
  }>({
    filters: null,
    query: '',
  })

  useEffect(() => {
    setFavoriteCount(adageUser?.favoritesCount ?? 0)
  }, [adageUser])

  return (
    <AdageUserContext.Provider
      value={{
        adageUser,
        favoritesCount,
        setFavoriteCount,
        filters,
        setFilters,
      }}
    >
      {children}
    </AdageUserContext.Provider>
  )
}
