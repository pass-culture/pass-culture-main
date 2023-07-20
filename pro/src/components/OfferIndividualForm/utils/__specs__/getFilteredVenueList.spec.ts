import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { OfferIndividualVenue } from 'core/Venue/types'

import { getFilteredVenueList } from '../getFilteredVenueList'

describe('getFilteredVenueList', () => {
  let virtualVenue: OfferIndividualVenue
  const firstVenueId = 1
  const secondVenueId = 2
  const thirdVenueId = 3

  const subCategories: OfferSubCategory[] = [
    {
      id: 'A-A',
      categoryId: 'A',
      proLabel: 'Sous catégorie online de A',
      isEvent: false,
      conditionalFields: [],
      canBeDuo: false,
      canBeEducational: false,
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
      isSelectable: true,
    },
    {
      id: 'A-B',
      categoryId: 'A',
      proLabel: 'Sous catégorie offline de A',
      isEvent: false,
      conditionalFields: [],
      canBeDuo: false,
      canBeEducational: false,
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
      isSelectable: true,
    },
    {
      id: 'A-C',
      categoryId: 'A',
      proLabel: 'Sous catégorie online or offline de A',
      isEvent: false,
      conditionalFields: [],
      canBeDuo: false,
      canBeEducational: false,
      canBeWithdrawable: false,
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
      reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
      isSelectable: true,
    },
  ]

  const venueList = [
    {
      id: secondVenueId,
      name: 'Lieu offline AA',
      managingOffererId: 1,
      isVirtual: false,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: false,
        audio: false,
        motor: false,
        none: true,
      },
      hasMissingReimbursementPoint: false,
      hasCreatedOffer: true,
    },
    {
      id: thirdVenueId,
      name: 'Lieu offline BB',
      managingOffererId: 1,
      isVirtual: false,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: false,
        audio: false,
        motor: false,
        none: true,
      },
      hasMissingReimbursementPoint: false,
      hasCreatedOffer: true,
    },
  ]

  beforeEach(() => {
    virtualVenue = {
      id: firstVenueId,
      name: 'Lieu online CC',
      managingOffererId: 1,
      isVirtual: true,
      withdrawalDetails: '',
      accessibility: {
        visual: false,
        mental: false,
        audio: false,
        motor: false,
        none: true,
      },
      hasMissingReimbursementPoint: false,
      hasCreatedOffer: true,
    }
  })

  it('should not filter venue on isVirtual when subCatagory is not selected', async () => {
    const result = getFilteredVenueList('', subCategories, [
      ...venueList,
      virtualVenue,
    ])
    expect(result.length).toEqual(3)
    expect(result[0].id).toEqual(secondVenueId)
    expect(result[1].id).toEqual(thirdVenueId)
    expect(result[2].id).toEqual(firstVenueId)
  })

  it('should not filter venue on isVirtual when subCatagory is ONLINE or OFFLINE', async () => {
    const result = getFilteredVenueList('A-C', subCategories, [
      ...venueList,
      virtualVenue,
    ])
    expect(result.length).toEqual(3)
    expect(result[0].id).toEqual(secondVenueId)
    expect(result[1].id).toEqual(thirdVenueId)
    expect(result[2].id).toEqual(firstVenueId)
  })

  it('should filter venue on isVirtual when subCatagory is ONLINE only', async () => {
    const result = getFilteredVenueList('A-A', subCategories, [
      ...venueList,
      virtualVenue,
    ])
    expect(result.length).toEqual(1)
    expect(result[0].id).toEqual(firstVenueId)
  })

  it('should filter venue on not isVirtual when subCatagory is OFFLINE only', async () => {
    const result = getFilteredVenueList('A-B', subCategories, [
      ...venueList,
      virtualVenue,
    ])
    expect(result.length).toEqual(2)
    expect(result[0].id).toEqual(secondVenueId)
    expect(result[1].id).toEqual(thirdVenueId)
  })
})
