import { GetOffererResponseModel } from 'apiClient/v1'

import { IOfferer } from '../types'

export const serializeOffererApi = (
  offerer: GetOffererResponseModel
): IOfferer => {
  return {
    id: offerer.id,
    siren: offerer.siren || '',
  }
}
