import { GetOffererResponseModel } from 'apiClient/v1'
import { useAdapter } from 'hooks'

import getOffererAdapter from './getOffererAdapter'

const useGetOfferer = (offererId?: string) =>
  useAdapter<GetOffererResponseModel, null>(() =>
    getOffererAdapter(Number(offererId))
  )

export default useGetOfferer
