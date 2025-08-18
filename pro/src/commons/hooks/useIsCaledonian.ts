import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { useSelector } from 'react-redux'

import { useOfferer } from './swr/useOfferer'

export const useIsCaledonian = () => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const { data: offerer } = useOfferer(selectedOffererId)
  return offerer?.isCaledonian ?? false
}
