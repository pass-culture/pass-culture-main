import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import getVenueCollectiveDataAdapter from '../getVenueCollectiveDataAdapter'

describe('getVenueCollectiveDataAdapter', () => {
  it('should return an error', async () => {
    // given
    jest.spyOn(api, 'getVenueCollectiveData').mockRejectedValue({
      status: 500,
    })

    // when
    const response = await getVenueCollectiveDataAdapter('V1')

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
  it('should return a collective data', async () => {
    const payload = {
      id: 'V1',
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
    jest.spyOn(api, 'getVenueCollectiveData').mockResolvedValueOnce(payload)

    // when
    const response = await getVenueCollectiveDataAdapter('V1')

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.payload).toStrictEqual(payload)
  })
})
