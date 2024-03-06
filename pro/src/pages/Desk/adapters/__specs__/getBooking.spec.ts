import { apiContremarque } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { MESSAGE_VARIANT } from 'pages/Desk/types'
import { defaultGetBookingResponse } from 'utils/individualApiFactories'

import { getBooking } from '..'

describe('getBooking', () => {
  describe('success', () => {
    it('should return serialized booking', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockResolvedValue(
        defaultGetBookingResponse
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        booking: defaultGetBookingResponse,
      })
    })
  })
  // The following tests describe the behaviour as if it is a failure (api is implemented this way) but it is in fact a feature
  // TODO : Api should return 200 with a booking object
  describe('failure', () => {
    it('should return already cancelled message when booking is already cancelled', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {
              booking_cancelled: 'already cancelled',
            },
            status: 410,
          } as ApiResult,
          'api error'
        )
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        error: {
          isTokenValidated: false,
          message: 'already cancelled',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })

    it('should return already validated message when booking is already validated', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 410,
          } as ApiResult,
          'api error'
        )
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        error: {
          isTokenValidated: true,
          message: 'api error',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })

    it('should return already reimbursed message when booking is already reimbursed', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {
              payment: 'already reimbursed',
            },
            status: 403,
          } as ApiResult,
          'api error'
        )
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        error: {
          isTokenValidated: false,
          message: 'already reimbursed',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })

    it('should return error message when the booking cant be validated and not reimbursed yet', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {
              booking: 'you will be able to validate later',
            },
            status: 403,
          } as ApiResult,
          ''
        )
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        error: {
          isTokenValidated: false,
          message: 'you will be able to validate later',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })

    it('should return the api error message for error status other that 410 and not handled when 403', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            body: {},
            status: 500,
          } as ApiResult,
          'api internal error'
        )
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        error: {
          isTokenValidated: false,
          message: 'api internal error',
          variant: MESSAGE_VARIANT.ERROR,
        },
      })
    })
  })
})
