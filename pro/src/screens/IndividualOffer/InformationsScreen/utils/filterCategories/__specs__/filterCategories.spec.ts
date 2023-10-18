import { CategoryResponseModel } from 'apiClient/v1'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import {
  individualOfferCategoryFactory,
  individualOfferSubCategoryFactory,
} from 'utils/individualApiFactories'

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
    (offerSubtype) => {
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
    (offerSubtype) => {
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
    (offerSubtype) => {
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
  let categories: CategoryResponseModel[]
  let subCategories: OfferSubCategory[]

  beforeEach(() => {
    categories = [
      individualOfferCategoryFactory({ id: 'A' }),
      individualOfferCategoryFactory({ id: 'B' }),
      individualOfferCategoryFactory({ id: 'C' }),
      individualOfferCategoryFactory({ id: 'D' }),
    ]
    subCategories = [
      individualOfferSubCategoryFactory({
        id: 'A-A',
        categoryId: 'A',
        isEvent: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'A-B',
        categoryId: 'A',
        isEvent: false,
        isSelectable: false,
      }),
      individualOfferSubCategoryFactory({
        id: 'B-A',
        categoryId: 'B',
        isEvent: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'C-A',
        categoryId: 'C',
        isEvent: true,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'C-B',
        categoryId: 'C',
        isEvent: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'C-C',
        categoryId: 'C',
        isEvent: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'C-D',
        categoryId: 'C',
        isEvent: true,
        isSelectable: false,
      }),
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
      filteredCategories.find((category) => category.id === 'D')
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
      filteredCategories.find((category) => category.id === 'D')
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

    expect(filteredCategories.map((category) => category.id)).toEqual([
      'A',
      'C',
    ])
    expect(filteredSubCategories.map((subCategory) => subCategory.id)).toEqual([
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

    expect(filteredCategories.map((category) => category.id)).toEqual([
      'B',
      'C',
    ])
    expect(filteredSubCategories.map((subCategory) => subCategory.id)).toEqual([
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

    expect(filteredCategories.map((category) => category.id)).toEqual([
      'A',
      'C',
    ])
    expect(filteredSubCategories.map((subCategory) => subCategory.id)).toEqual([
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

    expect(filteredCategories.map((category) => category.id)).toEqual(['B'])
    expect(filteredSubCategories.map((subCategory) => subCategory.id)).toEqual([
      'B-A',
    ])
  })
})
