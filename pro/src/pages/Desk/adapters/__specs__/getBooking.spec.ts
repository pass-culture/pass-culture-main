import { apiContremarque } from 'apiClient/api'
import { MESSAGE_VARIANT } from 'screens/Desk'
import { defaultBookingResponse } from 'utils/apiFactories'

import { getBooking } from '..'

describe('getBooking', () => {
  describe('success', () => {
    it('should return serialized booking', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockResolvedValue(
        defaultBookingResponse
      )

      const serializedBooking = await getBooking('test_booking_id')
      expect(serializedBooking).toStrictEqual({
        booking: defaultBookingResponse,
      })
    })
  })
  // The following tests describe the behaviour as if it is a failure (api is implemented this way) but it is in fact a feature
  // TODO : Api should return 200 with a booking object
  describe('failure', () => {
    it('should return already cancelled message when booking is already cancelled', async () => {
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue({
        status: 410,
        body: {
          booking_cancelled: 'already cancelled',
        },
        message: 'api error',
      })

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
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue({
        status: 410,
        body: {},
        message: 'api error',
      })

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
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue({
        status: 403,
        body: {
          payment: 'already reimbursed',
        },
      })

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
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue({
        status: 403,
        body: {
          booking: 'you will be able to validate later',
        },
      })

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
      vi.spyOn(apiContremarque, 'getBookingByTokenV2').mockRejectedValue({
        status: 500,
        body: {},
        message: 'api internal error',
      })

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
