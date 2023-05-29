import { useContext } from 'react'

import { AdageUserContext } from '../providers/AdageUserContext'

const useAdageUser = () => {
  const { adageUser } = useContext(AdageUserContext)
  /* istanbul ignore next: this is a safety check, shouldn't be possible to hit */
  if (!adageUser) {
    throw new Error(
      'useAdageUser must be used within an AdageUserContextProvider'
    )
  }

  return adageUser
}

export default useAdageUser
