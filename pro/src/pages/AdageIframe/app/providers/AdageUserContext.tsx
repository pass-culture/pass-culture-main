import {
  createContext,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
  useMemo,
  useState,
} from 'react'

import type { AuthenticatedResponse } from '@/apiClient/adage'

type AdageUserContextType = {
  adageUser: AuthenticatedResponse | null
  favoritesCount?: number
  setFavoritesCount?: Dispatch<SetStateAction<number>>
  institutionOfferCount?: number
  setInstitutionOfferCount?: Dispatch<SetStateAction<number>>
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
  const [favoritesCount, setFavoritesCount] = useState<number>(
    adageUser?.favoritesCount ?? 0
  )
  const [institutionOfferCount, setInstitutionOfferCount] = useState<number>(
    adageUser?.offersCount ?? 0
  )

  const contextValue = useMemo(
    () => ({
      adageUser,
      favoritesCount,
      setFavoritesCount,
      institutionOfferCount,
      setInstitutionOfferCount,
    }),
    [adageUser, favoritesCount, institutionOfferCount]
  )

  return (
    <AdageUserContext.Provider value={contextValue}>
      {children}
    </AdageUserContext.Provider>
  )
}
