import { GetOffererNameResponseModel } from 'apiClient/v1'

export type TOffererName = GetOffererNameResponseModel

export interface IOfferer {
  id: string
  siren: string
}
