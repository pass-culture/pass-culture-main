import { api } from 'apiClient/api'
import {
  ApiError,
  OfferAddressType,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { getStockCollectiveOfferTemplateAdapter } from '../getStockCollectiveOfferTemplateAdapter'

describe('getStockCollectiveOfferTemplateAdapter', () => {
  describe('getStockCollectiveOfferTemplateAdapter', () => {
    it('should return an error when API returns an error', async () => {
      // given
      vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              code: 'NO_BOOKING',
            },
          } as ApiResult,
          ''
        )
      )

      // when
      const response = await getStockCollectiveOfferTemplateAdapter(1)

      // then
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Une erreur est survenue lors de la récupération de votre offre'
      )
    })

    it('should not return an error when offer has been found', async () => {
      // given
      vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce({
        isActive: true,
        offerId: 1,
        bookingEmails: [],
        name: 'mon offre',
        contactEmail: 'mail',
        contactPhone: 'phone',
        dateCreated: 'date',
        description: 'description',
        domains: [],
        hasBookingLimitDatetimesPassed: false,
        interventionArea: [],
        isCancellable: true,
        isEditable: true,
        id: 1,
        offerVenue: {
          addressType: OfferAddressType.OFFERER_VENUE,
          otherAddress: '',
          venueId: 12,
        },
        status: OfferStatus.ACTIVE,
        students: [],
        subcategoryId: SubcategoryIdEnum.CONCERT,
        venue: {
          id: 1,
          managingOfferer: {
            id: 1,
            name: 'mon offerer',
          },
          name: 'mon lieu',
        },
        dates: { end: '', start: '' },
      })

      // when
      const response = await getStockCollectiveOfferTemplateAdapter(1)

      // then
      expect(response.isOk).toBeTruthy()
    })
  })
})
