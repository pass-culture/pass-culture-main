import { GetOffererResponseModel } from 'apiClient/v1'

import { Offerer } from '../types'

export const serializeOffererApi = (
  offerer: GetOffererResponseModel
): Offerer => {
  return <Offerer>{
    ...offerer,
  }
}
