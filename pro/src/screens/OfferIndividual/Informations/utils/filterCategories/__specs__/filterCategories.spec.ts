import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

import { CATEGORY_STATUS } from 'core/Offers'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { filterCategories } from '..'

describe('filterCategories', () => {
  let venue: TOfferIndividualVenue
  let categories: IOfferCategory[] = []
  let subCategories: IOfferSubCategory[] = []

  beforeEach(() => {
    venue = {
      id: 'A-A',
      managingOffererId: 'A',
      name: 'Lieu A de la structure A',
      isVirtual: true,
      withdrawalDetails: '',
    }
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
        isEvent: false,
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
        isEvent: false,
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
        isEvent: false,
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
        isEvent: false,
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
        isEvent: false,
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
      venue
    )

    expect(
      filteredCategories.find((c: IOfferCategory) => c.id === 'D')
    ).toBeUndefined()
    expect(
      filteredSubCategories.find((c: IOfferCategory) => c.id === 'C-D')
    ).toBeUndefined()
  })

  it('should return ONLINE categories and subCategories when venue is virtual', () => {
    venue = {
      ...venue,
      isVirtual: true,
    }
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      venue
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

  it('should return OFFLINE categories and subCategories when venue is physical', () => {
    venue = {
      ...venue,
      isVirtual: false,
    }
    const [filteredCategories, filteredSubCategories] = filterCategories(
      categories,
      subCategories,
      venue
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
})
