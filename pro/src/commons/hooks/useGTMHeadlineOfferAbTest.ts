import { useSelector } from 'react-redux'

import { selectCurrentUser } from 'commons/store/user/selectors'

export const useGTMHeadlineOfferAbTest = (): boolean => {
    const currentUser = useSelector(selectCurrentUser)
  
  return Boolean(currentUser && (currentUser.id % 2 === 0))
}
