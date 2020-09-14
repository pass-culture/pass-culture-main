import { signOut } from '../signOut'

jest.mock('../../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))


describe('signOut', () => {
  it('should call batchSDK', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )
    window.batchSDK = jest.fn()

    // when
    await signOut()

    // Then
    expect(window.batchSDK).toHaveBeenCalledWith(expect.any(Function))
  })

  it('should call fetch', async () => {
    // Given
    window.batchSDK = jest.fn()

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
