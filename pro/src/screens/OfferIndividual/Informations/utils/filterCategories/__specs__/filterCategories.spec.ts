import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

import { filterCategories } from '..'

describe('filterCategories', () => {
  let categories: IOfferCategory[]
  let subCategories: IOfferSubCategory[]

  beforeEach(() => {
    categories = [
      {
        id: 'A',
        proLabel: 'Catégorie uniquement online',
        isSelectable: true,
      },
      {
        id: 'B',
        proLabel: 'Catégorie uniquement offline',
        isSelectable: true,
      },
      {
        id: 'C',
        proLabel: 'Catégorie mixe online et offline',
        isSelectable: true,
      },
      {
        id: 'D',
        proLabel: 'Catégorie no disponible',
        isSelectable: false,
      },
    ]
    subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie de A',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'A-B',
        categoryId: 'A',
        proLabel: 'Sous catégorie de A non disponible',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: false,
      },
      {
        id: 'B-A',
        categoryId: 'B',
        proLabel: 'Sous catégorie de B',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-A',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-B',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-C',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'C-D',
        categoryId: 'C',
        proLabel: 'Sous catégorie de C',
        isEvent: true,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: false,
      },
    ]
  })

  it('should return selectable categories and subCategories', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE,
      null
    )

    expect(
      filteredCategories.find((c: IOfferCategory) => c.id === 'D')
    ).toBeUndefined()
    expect(
      filteredSubCategories.find((c: IOfferSubCategory) => c.id === 'C-D')
    ).toBeUndefined()
  })

  it('should return selectable categories and subCategories for CATEGORY_STATUS.ONLINE_OR_OFFLINE', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      null
    )

    expect(
      filteredCategories.find((c: IOfferCategory) => c.id === 'D')
    ).toBeUndefined()
    expect(
      filteredSubCategories.find((c: IOfferSubCategory) => c.id === 'C-D')
    ).toBeUndefined()
  })

  it('should return ONLINE categories and subCategories for CATEGORY_STATUS.ONLINE', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE,
      null
    )

    expect(filteredCategories.map((c: IOfferCategory) => c.id)).toEqual([
      'A',
      'C',
    ])
    expect(filteredSubCategories.map((s: IOfferSubCategory) => s.id)).toEqual([
      'A-A',
      'C-A',
      'C-B',
    ])
  })

  it('should return OFFLINE categories and subCategories CATEGORY_STATUS.OFFLINE', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.OFFLINE,
      null
    )

    expect(filteredCategories.map((c: IOfferCategory) => c.id)).toEqual([
      'B',
      'C',
    ])
    expect(filteredSubCategories.map((s: IOfferSubCategory) => s.id)).toEqual([
      'B-A',
      'C-A',
      'C-C',
    ])
  })

  it('should return filter subcategories that are events', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      true
    )

    expect(filteredCategories.map((c: IOfferCategory) => c.id)).toEqual([
      'A',
      'C',
    ])
    expect(filteredSubCategories.map((s: IOfferSubCategory) => s.id)).toEqual([
      'A-A',
      'C-A',
      'C-B',
      'C-C',
    ])
  })

  it('should return filter subcategories that are not events', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      false
    )

    expect(filteredCategories.map((c: IOfferCategory) => c.id)).toEqual(['B'])
    expect(filteredSubCategories.map((s: IOfferSubCategory) => s.id)).toEqual([
      'B-A',
    ])
  })
})
