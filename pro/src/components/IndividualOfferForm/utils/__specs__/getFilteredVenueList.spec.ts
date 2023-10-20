import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import {
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'

import {
  getFilteredVenueListByCategoryStatus,
  getFilteredVenueListBySubcategory,
} from '../getFilteredVenueList'

describe('getFilteredVenueList', () => {
  const virtualVenueId = 1
  const secondVenueId = 2
  const thirdVenueId = 3

  const subCategories: OfferSubCategory[] = [
    individualOfferSubCategoryFactory({
      id: 'ONLINE_ONLY',
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
    }),
    individualOfferSubCategoryFactory({
      id: 'OFFLINE_ONLY',
      onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
    }),
    individualOfferSubCategoryFactory({
      id: 'ONLINE_OR_OFFLINE',
      onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
    }),
  ]

  const virtualVenue = individualOfferVenueItemFactory({
    id: virtualVenueId,
    isVirtual: true,
  })

  const venueList = [
    individualOfferVenueItemFactory({
      id: secondVenueId,
      isVirtual: false,
    }),
    individualOfferVenueItemFactory({
      id: thirdVenueId,
      isVirtual: false,
    }),
  ]

  describe('getFilteredVenueListBySubcategory', () => {
    it('should return all venues when subCatagory is ONLINE or OFFLINE', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find((s) => s.id === 'ONLINE_OR_OFFLINE')
      )
      expect(result.length).toEqual(3)
      expect(result[0].id).toEqual(secondVenueId)
      expect(result[1].id).toEqual(thirdVenueId)
      expect(result[2].id).toEqual(virtualVenueId)
    })

    it('should return virtual venues when subCatagory is ONLINE only', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find((s) => s.id === 'ONLINE_ONLY')
      )
      expect(result.length).toEqual(1)
      expect(result[0].id).toEqual(virtualVenueId)
    })

    it('should return not virtual when subCatagory is OFFLINE only', async () => {
      const result = getFilteredVenueListBySubcategory(
        [...venueList, virtualVenue],
        subCategories.find((s) => s.id === 'OFFLINE_ONLY')
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
