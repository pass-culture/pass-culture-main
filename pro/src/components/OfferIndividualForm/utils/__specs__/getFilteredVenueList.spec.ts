import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'

import {
  getFilteredVenueListByCategoryStatus,
  getFilteredVenueListBySubcategory,
} from '../getFilteredVenueList'

describe('getFilteredVenueList', () => {
  const virtualVenueId = 1
  const secondVenueId = 2
  const thirdVenueId = 3

  const subCategories: OfferSubCategory[] = [
    {
      id: 'ONLINE_ONLY',
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
      id: 'OFFLINE_ONLY',
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
      id: 'ONLINE_OR_OFFLINE',
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

  const virtualVenue = {
    id: virtualVenueId,
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

  describe('getFilteredVenueListBySubcategory', () => {
    it('should return all venues when subCatagory is ONLINE or OFFLINE', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find(s => s.id === 'ONLINE_OR_OFFLINE')
      )
      expect(result.length).toEqual(3)
      expect(result[0].id).toEqual(secondVenueId)
      expect(result[1].id).toEqual(thirdVenueId)
      expect(result[2].id).toEqual(virtualVenueId)
    })

    it('should return virtual venues when subCatagory is ONLINE only', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find(s => s.id === 'ONLINE_ONLY')
      )
      expect(result.length).toEqual(1)
      expect(result[0].id).toEqual(virtualVenueId)
    })

    it('should return not virtual when subCatagory is OFFLINE only', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find(s => s.id === 'OFFLINE_ONLY')
      )
      expect(result.length).toEqual(2)
      expect(result[0].id).toEqual(secondVenueId)
      expect(result[1].id).toEqual(thirdVenueId)
    })
  })

  describe('getFilteredVenueListBySubcategory', () => {
    it('should return all venues when categoryStatus is ONLINE or OFFLINE', async () => {
      const result = getFilteredVenueListByCategoryStatus(
        [...venueList, virtualVenue],
        CATEGORY_STATUS.ONLINE_OR_OFFLINE
      )
      expect(result.length).toEqual(3)
      expect(result[0].id).toEqual(secondVenueId)
      expect(result[1].id).toEqual(thirdVenueId)
      expect(result[2].id).toEqual(virtualVenueId)
    })

    it('should return vitual venues when categoryStatus is ONLINE only', async () => {
      const result = getFilteredVenueListByCategoryStatus(
        [...venueList, virtualVenue],
        CATEGORY_STATUS.ONLINE
      )
      expect(result.length).toEqual(1)
      expect(result[0].id).toEqual(virtualVenueId)
    })

    it('should return not virtual when categoryStatus is OFFLINE only', async () => {
      const result = getFilteredVenueListByCategoryStatus(
        [...venueList, virtualVenue],
        CATEGORY_STATUS.OFFLINE
      )
      expect(result.length).toEqual(2)
      expect(result[0].id).toEqual(secondVenueId)
      expect(result[1].id).toEqual(thirdVenueId)
    })
  })
})
