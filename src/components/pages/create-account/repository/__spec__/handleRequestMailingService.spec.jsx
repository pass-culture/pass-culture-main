import { handleRequestMailingService } from '../handleRequestMailingService'

jest.mock('../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

const userInformations = {}

describe('when handle request mailing service', () => {
  it('should fetch API one time', async() => {
    // Given
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({}),
        ok: true,
      })
    )

    // when
    await handleRequestMailingService(userInformations)

    // Then
    expect(global.fetch).toHaveBeenCalledTimes(1)
  })
})
