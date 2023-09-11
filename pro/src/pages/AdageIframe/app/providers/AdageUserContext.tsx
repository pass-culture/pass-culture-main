import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { AuthenticatedResponse } from 'apiClient/adage'

type AdageUserContextType = {
  adageUser: (AuthenticatedResponse & { favoriteCount?: number }) | null
  favoriteCount?: number
  setFavoriteCount?: Dispatch<SetStateAction<number>>
}

export const AdageUserContext = createContext<AdageUserContextType>({
  adageUser: null,
})

export const AdageUserContextProvider = ({
  children,
  adageUser,
}: {
  children: ReactNode
  adageUser: AdageUserContextType['adageUser']
}): JSX.Element => {
  const [favoriteCount, setFavoriteCount] = useState<number>(0)

  useEffect(() => {
    setFavoriteCount(adageUser?.favoriteCount ?? 0)
  }, [adageUser])

  const value = useMemo(
    () => ({
      adageUser,
      favoriteCount,
      setFavoriteCount,
    }),
    [adageUser, favoriteCount]
  )

  return (
    <AdageUserContext.Provider value={value}>
      {children}
    </AdageUserContext.Provider>
  )
}
