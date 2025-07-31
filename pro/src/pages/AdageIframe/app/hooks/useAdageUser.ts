import { useContext } from 'react'

import { assertOrFrontendError } from 'commons/errors/assertOrFrontendError'

import { AdageUserContext } from '../providers/AdageUserContext'

export const useAdageUser = () => {
  const {
    adageUser,
    setFavoriteCount,
    favoritesCount,
    institutionOfferCount,
    setInstitutionOfferCount,
  } = useContext(AdageUserContext)
  assertOrFrontendError(
    adageUser,
    '`useAdageUser` must be used within an `AdageUserContextProvider`.'
  )

  return {
    adageUser,
    setFavoriteCount,
    favoritesCount,
    institutionOfferCount,
    setInstitutionOfferCount,
  }
}
