import { ApiError } from '@/apiClient//v1'
import { ApiRequestOptions } from '@/apiClient//v1/core/ApiRequestOptions'
import { ApiResult } from '@/apiClient//v1/core/ApiResult'

import { getBookingFailure } from '../getBookingFailure'

describe('getBookingFailure', () => {
  it('should return already cancelled message when booking is already cancelled', () => {
    const failure = getBookingFailure(
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
    expect(failure).toStrictEqual({
      isTokenValidated: false,
      message: 'already cancelled',
    })
  })

  it('should return already validated message when booking is already validated', () => {
    const failure = getBookingFailure(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {},
          status: 410,
        } as ApiResult,
        'api error'
      )
    )
    expect(failure).toStrictEqual({
      isTokenValidated: true,
      message: 'api error',
    })
  })

  it('should return already reimbursed message when booking is already reimbursed', () => {
    const failure = getBookingFailure(
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

    expect(failure).toStrictEqual({
      isTokenValidated: false,
      message: 'already reimbursed',
    })
  })

  it('should return error message when the booking cant be validated and not reimbursed yet', () => {
    const failure = getBookingFailure(
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

    expect(failure).toStrictEqual({
      isTokenValidated: false,
      message: 'you will be able to validate later',
    })
  })

  it('should return the api error message for error status other that 410 and not handled when 403', () => {
    const failure = getBookingFailure(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {},
          status: 500,
        } as ApiResult,
        'api internal error'
      )
    )
    expect(failure).toStrictEqual({
      isTokenValidated: false,
      message: 'api internal error',
    })
  })
})
