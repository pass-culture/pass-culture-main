import { requestData } from 'redux-saga-data'
import { isValidToken } from '../client'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))

describe('src | utils | http | isTokenValid', () => {
  it('should contact the API to check if token exists', () => {
    // given
    const token = 'my-token-to-test'

    // when
    isValidToken(token)

    // then
    expect(requestData).toHaveBeenCalledWith({
      apiPath: '/users/token/my-token-to-test',
      handleFail: expect.any(Function),
      handleSuccess: expect.any(Function),
      method: 'GET',
    })
  })

  describe('when the token does not exist', () => {
    it('should return false', async () => {
      // given
      const token = 'my-token-to-test'
      requestData.mockImplementation(({ handleFail }) => handleFail())

      // when
      const result = await isValidToken(token)

      // then
      expect(result).toBe(false)
    })
  })

  describe('when the token exists', () => {
    it('should return true', async () => {
      // given
      const token = 'my-token-to-test'
      requestData.mockImplementation(({ handleSuccess }) => handleSuccess())

      // when
      const result = await isValidToken(token)

      // then
      expect(result).toBe(true)
    })
  })
})
