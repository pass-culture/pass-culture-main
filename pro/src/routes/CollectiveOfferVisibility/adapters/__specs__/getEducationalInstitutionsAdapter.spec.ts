import { api } from 'apiClient/api'
import { EducationalInstitutionsResponseModel } from 'apiClient/v1'

import { getEducationalInstitutionsAdapter } from '../getEducationalInstitutionsAdapter'

describe('getEducationalInstitutionsAdapter', () => {
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
        },
        {
          id: 24,
          name: 'Institution 2',
          postalCode: '75005',
          city: 'Paris',
          phoneNumber: '',
        },
        {
          id: 42,
          name: 'Institution 3',
          postalCode: '33000',
          city: 'Bordeaux',
          phoneNumber: '',
        },
      ],
    }
  })

  it('should return an error when the institutions could not be retrieved', async () => {
    jest.spyOn(api, 'getEducationalInstitutions').mockRejectedValueOnce(null)
    const response = await getEducationalInstitutionsAdapter()
    expect(response.isOk).toBe(false)
    expect(response.message).toBe(
      'Une erreur est survenue lors du chargement des données'
    )
  })
  it('should return an error if any page returns an error', async () => {
    jest
      .spyOn(api, 'getEducationalInstitutions')
      .mockResolvedValueOnce(institutionsPaginated)
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 2 })
      .mockRejectedValueOnce(null)
    const response = await getEducationalInstitutionsAdapter()
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors du chargement des données'
    )
  })
  it('should return a confirmation when all results are retrieved', async () => {
    jest
      .spyOn(api, 'getEducationalInstitutions')
      .mockResolvedValueOnce(institutionsPaginated)
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 2 })
      .mockResolvedValueOnce({ ...institutionsPaginated, page: 3 })
    const response = await getEducationalInstitutionsAdapter()
    expect(response.isOk).toBeTruthy()
    expect(response.payload?.institutions.length).toBe(9)
  })
})
