import { IAccessibiltyFormValues } from 'core/shared'
import { WithdrawalTypeEnum } from 'apiClient/v1'

export interface IOfferIndividualFormValues {
  isEvent?: boolean
  subCategoryFields: string[]
  title: string
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
}
