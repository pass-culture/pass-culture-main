import { useSelector } from 'react-redux'

import { GetOffererNameResponseModel } from 'apiClient/v1'
import { selectOfferersNames } from 'store/offererNames/selectors'

const useOfferersNames = (): GetOffererNameResponseModel[] => {
  return useSelector(selectOfferersNames)
}

export default useOfferersNames
