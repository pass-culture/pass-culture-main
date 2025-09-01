import {
  type CategoryResponseModel,
  SubcategoryIdEnum,
  type SubcategoryResponseModel,
} from '@/apiClient/v1'
import { REIMBURSEMENT_RULES } from '@/commons/core/Finances/constants'
import { CATEGORY_STATUS } from '@/commons/core/Offers/constants'
import {
  categoryFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'

// This type is used to ensure that the subcategory has an `id` of type `SubcategoryIdEnum`
// (which avoids adding `as SubcategoryIdEnum` everywhere).
type SubcategoryResponseModelWithId = Omit<SubcategoryResponseModel, 'id'> & {
  id: SubcategoryIdEnum
}
const typedSubcategoryFactory = subcategoryFactory as (
  customSubcategory?: Partial<SubcategoryResponseModel>
) => SubcategoryResponseModelWithId

export const MOCKED_CATEGORY = {
  A: categoryFactory({
    id: SubcategoryIdEnum.EVENEMENT_CINE,
    proLabel: 'Catégorie A',
  }),
} satisfies Record<string, CategoryResponseModel>

export const MOCKED_CATEGORIES = Object.values(MOCKED_CATEGORY)

export const MOCKED_SUBCATEGORY = {
  EVENT_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.EVENEMENT_CINE,
    categoryId: MOCKED_CATEGORY.A.id,
    isEvent: true,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  EVENT_ONLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.LIVESTREAM_EVENEMENT,
    categoryId: MOCKED_CATEGORY.A.id,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  // TODO (igabriele, 2025-07-30): Remove this once it's removed from the API.
  /** @deprecated `ONLINE_OR_OFFLINE` should never exist anymore in production. */
  EVENT_ONLINE_AND_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.SALON,
    categoryId: MOCKED_CATEGORY.A.id,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
  }),
  NON_EVENT_OFFLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.ABO_PRATIQUE_ART,
    categoryId: MOCKED_CATEGORY.A.id,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  NON_EVENT_OFFLINE_WITH_EAN: typedSubcategoryFactory({
    id: SubcategoryIdEnum.LIVRE_PAPIER,
    categoryId: MOCKED_CATEGORY.A.id,
    conditionalFields: ['ean'],
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  NON_EVENT_ONLINE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.ABO_LIVRE_NUMERIQUE,
    categoryId: MOCKED_CATEGORY.A.id,
    isEvent: false,
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  NON_REFUNDABLE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.CINE_PLEIN_AIR,
    categoryId: MOCKED_CATEGORY.A.id,
    reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
  }),
  WIDTHDRAWABLE: typedSubcategoryFactory({
    id: SubcategoryIdEnum.CONCERT,
    categoryId: MOCKED_CATEGORY.A.id,
    canBeWithdrawable: true,
  }),
} satisfies Record<string, SubcategoryResponseModelWithId>

export const MOCKED_SUBCATEGORIES = Object.values(MOCKED_SUBCATEGORY)
