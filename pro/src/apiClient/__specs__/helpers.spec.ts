import '@testing-library/jest-dom'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { getErrorCode } from '../helpers'

describe('test apiClient:helpers', () => {
  describe('test getErrorCode', () => {
    it("should return ApiError body's error code", () => {
      const request: ApiRequestOptions = {
        method: 'GET',
        url: 'http://test.url',
      }
      const response: ApiResult = {
        url: 'http://test.url',
        ok: false,
        status: 501,
        statusText: 'UNAUTHORIZED',
        body: {
          error: "Vous n'etes pas authorisé à voir cette page.",
          code: 'UNAUTHORIZED_ACCESS',
        },
      }
      const error = new ApiError(
        request,
        response,
        "Vous n'etes pas authorisé à voir cette page."
      )

      const errorCode = getErrorCode(error)
      expect(errorCode).toBe('UNAUTHORIZED_ACCESS')
    })
  })
})
