import { api } from 'apiClient/api'
import { ApiError, OfferAddressType, StudentLevels } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import getCollectiveBookingAdapter from '../getCollectiveBookingAdapter'

jest.mock('apiClient/api')

describe('getCollectiveBookingAdapter', () => {
  it('should return an error', async () => {
    jest
      .spyOn(api, 'getCollectiveBookingById')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, {} as ApiResult, '')
      )

    expect(await getCollectiveBookingAdapter('bookingId')).toStrictEqual({
      isOk: false,
      message: GET_DATA_ERROR_MESSAGE,
      payload: null,
    })
  })

  it('should return booking details', async () => {
    const booking = {
      beginningDatetime: '2022-01-01T00:00:00',
      educationalInstitution: {
        city: 'Paris',
        id: 1,
        institutionType: 'COLLEGE',
        name: 'NOM DU COLLEGE',
        postalCode: '75017',
        phoneNumber: '',
      },
      educationalRedactor: {
        civility: 'M',
        email: 'john@doe.com',
        firstName: 'John',
        id: 1,
        lastName: 'Doe',
      },
      id: 1,
      offerVenue: {
        addressType: OfferAddressType.OTHER,
        otherAddress: 'Quelque part',
        venueId: '',
      },
      price: 100,
      students: [StudentLevels.CAP_1RE_ANN_E],
      venuePostalCode: '75017',
      numberOfTickets: 10,
      isCancellable: true,
    }

    jest.spyOn(api, 'getCollectiveBookingById').mockResolvedValueOnce(booking)

    expect(await getCollectiveBookingAdapter('bookingId')).toStrictEqual({
      isOk: true,
      message: '',
      payload: booking,
    })
  })
})
