import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'

export type OffererName = GetOffererNameResponseModel

export interface Offerer extends GetOffererResponseModel {}
