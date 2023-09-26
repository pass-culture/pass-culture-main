import { REIMBURSEMENT_RULES } from 'core/Finances'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import { OfferCategory, OfferSubCategory } from 'core/Offers/types'

import {
  getOfferSubtypeFromParam,
  getCategoryStatusFromOfferSubtype,
  filterCategories,
} from '../filterCategories'

describe('getOfferSubtypeFromParam', () => {
  const cases = [
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD,
  ]

  it.each(cases)(
    'should deduce the offer subtype %s from the query param',
    offerSubtype => {
      expect(getOfferSubtypeFromParam(offerSubtype)).toBe(offerSubtype)
    }
  )

  it('should return null if the query param is not a valid offer subtype', () => {
    expect(getOfferSubtypeFromParam('Not a valid offer subtype')).toBe(null)
  })

  it('should return null if the query param is null', () => {
    expect(getOfferSubtypeFromParam(null)).toBe(null)
  })
})

describe('getCategoryStatusFromOfferSubtype', () => {
  const physicalCases = [
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
  ]

  it.each(physicalCases)(
    'should return category offline for physical cases',
    offerSubtype => {
      expect(getCategoryStatusFromOfferSubtype(offerSubtype)).toBe(
        CATEGORY_STATUS.OFFLINE
      )
    }
  )
  const virtualCases = [
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD,
  ]

  it.each(virtualCases)(
    'should return category online for virtual cases',
    offerSubtype => {
      expect(getCategoryStatusFromOfferSubtype(offerSubtype)).toBe(
        CATEGORY_STATUS.ONLINE
      )
    }
  )
  it('should return both category when subtype is not defined', () => {
    expect(getCategoryStatusFromOfferSubtype(null)).toBe(
      CATEGORY_STATUS.ONLINE_OR_OFFLINE
    )
  })
})

describe('filterCategories', () => {
  let categories: OfferCategory[]
  let subCategories: OfferSubCategory[]

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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
        canBeWithdrawable: false,
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
      filteredCategories.find(category => category.id === 'D')
    ).toBeUndefined()
    expect(
      filteredSubCategories.find((c: OfferSubCategory) => c.id === 'C-D')
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
      filteredCategories.find(category => category.id === 'D')
    ).toBeUndefined()
    expect(
      filteredSubCategories.find((c: OfferSubCategory) => c.id === 'C-D')
    ).toBeUndefined()
  })

  it('should return ONLINE categories and subCategories for CATEGORY_STATUS.ONLINE', () => {
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      CATEGORY_STATUS.ONLINE,
      null
    )

    expect(filteredCategories.map(category => category.id)).toEqual(['A', 'C'])
    expect(filteredSubCategories.map(subCategory => subCategory.id)).toEqual([
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

    expect(filteredCategories.map(category => category.id)).toEqual(['B', 'C'])
    expect(filteredSubCategories.map(subCategory => subCategory.id)).toEqual([
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

    expect(filteredCategories.map(category => category.id)).toEqual(['A', 'C'])
    expect(filteredSubCategories.map(subCategory => subCategory.id)).toEqual([
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

    expect(filteredCategories.map(category => category.id)).toEqual(['B'])
    expect(filteredSubCategories.map(subCategory => subCategory.id)).toEqual([
      'B-A',
    ])
  })
})
