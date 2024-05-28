import { api } from 'apiClient/api'
import { EducationalInstitutionsResponseModel } from 'apiClient/v1'

import { getEducationalInstitutions } from '../getEducationalInstitutions'

describe('getEducationalInstitutions', () => {
  let institutionsPaginated: EducationalInstitutionsResponseModel
  beforeEach(() => {
    institutionsPaginated = {
      pages: 3,
      page: 1,
      total: 9,
      educationalInstitutions: [
        {
          id: 12,
          name: 'Institution 1',
          postalCode: '91190',
          city: 'Gif-sur-Yvette',
          phoneNumber: '',
          institutionId: 'ABCDED11',
        },
        {
          id: 24,
          name: 'Institution 2',
          postalCode: '75005',
          city: 'Paris',
          phoneNumber: '',
          institutionId: 'ABCDED12',
        },
        {
          id: 42,
          name: 'Institution 3',
          postalCode: '33000',
          city: 'Bordeaux',
          phoneNumber: '',
          institutionId: 'ABCDED13',
        },
      ],
    }
  })

  it('should return an error when the institutions could not be retrieved', async () => {
    vi.spyOn(api, 'getEducationalInstitutions').mockRejectedValueOnce(
      new Error()
    )

    await expect(() => getEducationalInstitutions()).rejects.toThrowError()
  })

  it('should return an error if any page returns an error', async () => {
    vi.spyOn(api, 'getEducationalInstitutions')
      .mockResolvedValueOnce(institutionsPaginated)
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 2 })
      .mockRejectedValueOnce(new Error())

    await expect(() => getEducationalInstitutions()).rejects.toThrowError()
  })

  it('should return a confirmation when all results are retrieved', async () => {
    vi.spyOn(api, 'getEducationalInstitutions')
      .mockResolvedValueOnce(institutionsPaginated)
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 2 })
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 3 })
    const response = await getEducationalInstitutions()
    expect(response.length).toBe(9)
  })
})
