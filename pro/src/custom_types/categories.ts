import { CATEGORY_STATUS } from 'core/Offers'

export type Category = {
  id: string
  proLabel: string
  isSelectable: boolean
}

export type SubCategory = {
  id: string
  categoryId: string
  proLabel: string
  appLabel: string
  searchGroupName: string
  isEvent: boolean
  conditionalFields: string[]
  canExpire: boolean
  canBeDuo: boolean
  canBeEducational: boolean
  onlineOfflinePlatform: CATEGORY_STATUS
  isDigitalDeposit: boolean
  isPhysicalDeposit: boolean
  reimbursementRule: string
  isSelectable: boolean
}
