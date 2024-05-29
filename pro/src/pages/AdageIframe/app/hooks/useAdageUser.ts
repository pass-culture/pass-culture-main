import { useContext } from 'react'

import { AdageUserContext } from '../providers/AdageUserContext'

export const useAdageUser = () => {
  const {
    adageUser,
    setFavoriteCount,
    favoritesCount,
    institutionOfferCount,
    setInstitutionOfferCount,
  } = useContext(AdageUserContext)
  /* istanbul ignore next: this is a safety check, shouldn't be possible to hit */
  if (!adageUser) {
    throw new Error(
      'useAdageUser must be used within an AdageUserContextProvider'
    )
  }

  return {
    adageUser,
    setFavoriteCount,
    favoritesCount,
    institutionOfferCount,
    setInstitutionOfferCount,
  }
}
