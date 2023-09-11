import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useState,
} from 'react'

import { AuthenticatedResponse } from 'apiClient/adage'

type AdageUserContextType = {
  adageUser: AuthenticatedResponse | null
  favoritesCount?: number
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
  const [favoritesCount, setFavoriteCount] = useState<number>(0)

  useEffect(() => {
    setFavoriteCount(adageUser?.favoritesCount ?? 0)
  }, [adageUser])

  return (
    <AdageUserContext.Provider
      value={{
        adageUser,
        favoritesCount,
        setFavoriteCount,
      }}
    >
      {children}
    </AdageUserContext.Provider>
  )
}
