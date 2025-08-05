import { SubcategoryIdEnum, type SubcategoryResponseModel } from 'apiClient/v1'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { subcategoryFactory } from 'commons/utils/factories/individualApiFactories'

type SubcategoryResponseModelWithId = Omit<SubcategoryResponseModel, 'id'> & {
  id: SubcategoryIdEnum
}

const typedSubcategoryFactory = subcategoryFactory as (
  customSubcategory?: Partial<SubcategoryResponseModel>
) => SubcategoryResponseModelWithId

export const MOCK_SUB_CATEGORY = {
  EVENT_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.EVENEMENT_CINE,
    isEvent: true,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  EVENT_ONLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.LIVESTREAM_EVENEMENT,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  // TODO (igabriele, 2025-07-30): Remove this once it's removed from the API.
  /** @deprecated `ONLINE_OR_OFFLINE` should never exist anymore in production. */
  EVENT_ONLINE_AND_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.SALON,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
  }),
  NON_EVENT_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.LIVRE_PAPIER,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  NON_EVENT_ONLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.ABO_LIVRE_NUMERIQUE,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  NON_REFUNDABLE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.CINE_PLEIN_AIR,
    reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
  }),
  WIDTHDRAWABLE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.CONCERT,
    canBeWithdrawable: true,
  }),
} satisfies Record<string, SubcategoryResponseModelWithId>

export const MOCK_SUB_CATEGORIES = Object.values(MOCK_SUB_CATEGORY)
