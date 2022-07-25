import { AdageCulturalPartnerResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { api } from 'apiClient/api'
import getCulturalPartnerAdapter from '../getCulturalPartnerAdapter'

describe('getCulturalPartnerAdapter', () => {
  it('should return an error', async () => {
    // given
    jest.spyOn(api, 'getEducationalPartner').mockRejectedValue({
      status: 500,
    })

    // when
    const response = await getCulturalPartnerAdapter('V1')

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
  })
  it('should return a cultural partner', async () => {
    const payload: AdageCulturalPartnerResponseModel = {
      id: 1,
      statutId: 3,
      siteWeb: 'www.toto.com',
      domaineIds: [1, 2],
    }
    // given
    jest.spyOn(api, 'getEducationalPartner').mockResolvedValueOnce(payload)

    // when
    const response = await getCulturalPartnerAdapter('siret')

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.payload).toStrictEqual(payload)
  })
})
