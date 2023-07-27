import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import getVenueCollectiveDataAdapter from '../getVenueCollectiveDataAdapter'

describe('getVenueCollectiveDataAdapter', () => {
  const venueId = 1
  it('should return an error', async () => {
    // given
    vi.spyOn(api, 'getVenueCollectiveData').mockRejectedValue({
      status: 500,
    })

    // when
    const response = await getVenueCollectiveDataAdapter(venueId)

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
  it('should return a collective data', async () => {
    const payload = {
      id: 'AE',
      collectiveDescription: '',
      collectiveDomains: [],
      collectiveEmail: '',
      collectiveLegalStatus: null,
      collectiveInterventionArea: [],
      collectiveNetwork: [],
      collectivePhone: '',
      collectiveStudents: [],
      collectiveWebsite: '',
    }
    // given
    vi.spyOn(api, 'getVenueCollectiveData').mockResolvedValueOnce(payload)

    // when
    const response = await getVenueCollectiveDataAdapter(venueId)

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.payload).toStrictEqual(payload)
  })
})
