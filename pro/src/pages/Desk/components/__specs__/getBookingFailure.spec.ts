import { HTTP_STATUS } from '@/apiClient/helpers'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'

import { getBookingFailure } from '../getBookingFailure'

const buildApiError = ({
  status,
  body = {},
  message = 'api error',
}: {
  status: number
  body?: Record<string, unknown>
  message?: string
}) =>
  new ApiError({} as ApiRequestOptions, { body, status } as ApiResult, message)

describe('getBookingFailure', () => {
  /* ---------------------------------------------------------------------- */
  /*                              HTTP 410 (GONE)                           */
  /* ---------------------------------------------------------------------- */

  describe('when status is HTTP_STATUS.GONE (410)', () => {
    it('returns cancelled message when booking is already cancelled', () => {
      const failure = getBookingFailure(
        buildApiError({
          status: HTTP_STATUS.GONE,
          body: { booking_cancelled: 'already cancelled' },
        })
      )

      expect(failure).toStrictEqual({
        isTokenValidated: false,
        message: 'already cancelled',
      })
    })

    it('returns validated state when booking already validated', () => {
      const failure = getBookingFailure(
        buildApiError({
          status: HTTP_STATUS.GONE,
        })
      )

      expect(failure).toEqual({
        isTokenValidated: true,
        message:
          "Cette contremarque a été validée. En l'invalidant vous indiquez qu'elle n'a pas été utilisée et vous ne serez pas remboursé.",
      })
    })
  })

  /* ---------------------------------------------------------------------- */
  /*                            HTTP 403 (FORBIDDEN)                        */
  /* ---------------------------------------------------------------------- */

  describe('when status is HTTP_STATUS.FORBIDDEN (403)', () => {
    it('returns reimbursed message when booking already reimbursed', () => {
      const failure = getBookingFailure(
        buildApiError({
          status: HTTP_STATUS.FORBIDDEN,
          body: { payment: 'already reimbursed' },
        })
      )

      expect(failure).toStrictEqual({
        isTokenValidated: false,
        message: 'already reimbursed',
      })
    })

    it('returns cant-be-validated message', () => {
      const failure = getBookingFailure(
        buildApiError({
          status: HTTP_STATUS.FORBIDDEN,
          body: { booking: 'you will be able to validate later' },
          message: '',
        })
      )

      expect(failure).toStrictEqual({
        isTokenValidated: false,
        message: 'you will be able to validate later',
      })
    })
  })
})
