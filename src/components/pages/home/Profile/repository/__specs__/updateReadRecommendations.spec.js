import { updateReadRecommendations } from '../updateReadRecommendations'

jest.mock('../../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

const readRecommendations = {}

describe('when response from API', () => {
  it('should call fetch properly', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      })
    )

    // when
    await updateReadRecommendations(readRecommendations)

    // Then
    expect(global.fetch).toHaveBeenCalledWith('my-localhost/recommendations/read', {
      body: JSON.stringify(readRecommendations),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'PUT',
    })
  })
})

describe('when status is other that 200', () => {
  it('should stop the app', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
        ok: false,
        status: 582,
        statusText: 'Error',
      })
    )

    // When
    const expected = updateReadRecommendations(readRecommendations)

    // When Then
    await expect(expected).rejects.toThrow('Status: 582, Status text: Error')
  })
})

describe('when no response from API', () => {
  it('should stop the app', async () => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() => Promise.reject('API is down'))

    // when
    const expected = updateReadRecommendations(readRecommendations)

    // Then
    await expect(expected).rejects.toThrow('API is down')
  })
})
