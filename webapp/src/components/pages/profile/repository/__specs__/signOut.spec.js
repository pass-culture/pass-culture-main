import { signOut } from '../signOut'

jest.mock('../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

jest.mock('../../../../../notifications/setUpBatchSDK', () => ({
  getBatchSDK: jest.fn()
}))

describe('signOut', () => {
  it('should call batchSDK', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )
    jest.spyOn(window, 'batchSDK').mockImplementation()

    // when
    await signOut()

    // Then
    expect(window.batchSDK).toHaveBeenCalledWith(expect.any(Function))
  })

  it('should call fetch', async () => {
    // Given
    jest.spyOn(window, 'batchSDK').mockImplementation()

    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )

    // when
    await signOut()

    // Then
    expect(global.fetch).toHaveBeenCalledWith('my-localhost/users/signout', {
      credentials: 'include',
    })
  })
})
