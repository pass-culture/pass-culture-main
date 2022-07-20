import { IAccessibiltyFormValues } from 'core/shared'

export interface IOfferIndividualFormValues {
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
  withdrawalDetails: string | null
  withdrawalType: string
  withdrawalDelay: string
  accessibility: IAccessibiltyFormValues
}
