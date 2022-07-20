import { WithdrawalTypeEnum } from 'apiClient/v1'
import { IAccessibiltyFormValues } from 'core/shared'

export interface IOfferIndividualFormValues {
  isEvent?: boolean
  subCategoryFields: string[]
  name: string
  description: string
  offererId: string
  venueId: string
  isNational: boolean
  categoryId: string
  subcategoryId: string
  showType: string
  showSubType: string
  musicType: string
  musicSubType: string
  withdrawalDetails: string
  withdrawalDelay?: number | null
  withdrawalType?: WithdrawalTypeEnum | null
  accessibility: IAccessibiltyFormValues
  author?: string | null
  isbn?: string | null
  performer?: string | null
  speaker?: string | null
  stageDirector?: string | null
  visa?: string | null
}
