import { api } from 'apiClient/api'

import { getEducationalRedactorsAdapter } from '../getEducationalRedactorAdapter'

describe('getEducationalRedactorAdapter', () => {
  let allRedactors: any
  beforeEach(() => {
    allRedactors = [
      {
        email: 'maria.sklodowska@example.com',
        gender: 'Mme.',
        name: 'SKLODOWSKA',
        surname: 'MARIA',
      },
      {
        email: 'confusion.raymar@example.com',
        gender: 'M.',
        name: 'HENMAR',
        surname: 'CONFUSION',
      },
    ]
  })

  it('should return an error when the institutions could not be retrieved', async () => {
    vi.spyOn(
      api,
      'getAutocompleteEducationalRedactorsForUai'
    ).mockRejectedValueOnce(null)
    const response = await getEducationalRedactorsAdapter({
      uai: '0470009E',
      candidate: 'mar',
    })
    expect(response.isOk).toBe(false)
    expect(response.message).toBe(
      'Une erreur est survenue lors du chargement des données'
    )
  })
  it('should return a confirmation when all results are retrieved', async () => {
    vi.spyOn(
      api,
      'getAutocompleteEducationalRedactorsForUai'
    ).mockResolvedValueOnce(allRedactors)
    const response = await getEducationalRedactorsAdapter({
      uai: '0470009E',
      candidate: 'mar',
    })
    expect(response.isOk).toBeTruthy()
    expect(response.payload?.length).toBe(2)
  })
})
