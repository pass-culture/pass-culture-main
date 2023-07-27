import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { getEducationalDomainsAdapter } from '../getEducationalDomainsAdapter'

describe('getEducationalDomainsAdapter', () => {
  it('should return an error when API returns an error', async () => {
    vi.spyOn(api, 'listEducationalDomains').mockRejectedValueOnce(null)
    const response = await getEducationalDomainsAdapter()

    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
  })

  it('should return a list of domains', async () => {
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValueOnce([
      { id: 1, name: 'Cinéma' },
      { id: 2, name: 'Musique' },
    ])

    const response = await getEducationalDomainsAdapter()

    expect(response.isOk).toBeTruthy()
    expect(response.payload).toEqual([
      { value: '1', label: 'Cinéma' },
      { value: '2', label: 'Musique' },
    ])
  })
})
