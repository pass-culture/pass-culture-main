import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'

export type OffererName = GetOffererNameResponseModel

export interface Offerer extends GetOffererResponseModel {
  dateModifiedAtLastProvider?: string | null
  fieldsUpdated: Array<string>
  idAtProviders?: string | null
  lastProviderId?: string | null
  siren: string
  dsToken: string
}
