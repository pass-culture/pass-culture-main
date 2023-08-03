import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import { getNationalProgramsAdapter } from '../getNationalProgramAdapter'

describe('getNationalProgramsAdapter', () => {
  it('should return an error when API returns an error', async () => {
    vi.spyOn(api, 'getNationalPrograms').mockRejectedValueOnce(null)
    const response = await getNationalProgramsAdapter()

    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
  })

  it('should return a list of national program', async () => {
    vi.spyOn(api, 'getNationalPrograms').mockResolvedValueOnce([
      { id: 1, name: 'Marseille en grand' },
      { id: 2, name: 'Collège au ciné' },
    ])

    const response = await getNationalProgramsAdapter()

    expect(response.isOk).toBeTruthy()
    expect(response.payload).toEqual([
      { value: 1, label: 'Marseille en grand' },
      { value: 2, label: 'Collège au ciné' },
    ])
  })
})
