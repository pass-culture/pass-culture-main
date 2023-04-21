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
      jest.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce(
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
      jest.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce({
        id: 'A1',
        isActive: true,
        offerId: 'A1',
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
        nonHumanizedId: 1,
        offerVenue: {
          addressType: OfferAddressType.OFFERER_VENUE,
          otherAddress: '',
          venueId: 'A1',
        },
        status: OfferStatus.ACTIVE,
        students: [],
        subcategoryId: SubcategoryIdEnum.CONCERT,
        venue: {
          fieldsUpdated: [],
          id: 'A1',
          isVirtual: false,
          nonHumanizedId: 1,
          managingOfferer: {
            city: 'Vélizy',
            dateCreated: 'date',
            id: '1',
            isActive: true,
            isValidated: true,
            name: 'mon offerer',
            postalCode: '78sang40',
            thumbCount: 1,
          },
          managingOffererId: 'A1',
          name: 'mon lieu',
          thumbCount: 1,
        },
        venueId: 'A1',
      })

      // when
      const response = await getStockCollectiveOfferTemplateAdapter(1)

      // then
      expect(response.isOk).toBeTruthy()
    })
  })
})
