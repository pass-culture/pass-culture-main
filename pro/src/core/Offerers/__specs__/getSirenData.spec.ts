import { api } from 'apiClient/api'
import { isError } from 'apiClient/helpers'
import { ApiError } from 'apiClient/v1'
import { getSirenData } from 'core/Offerers/getSirenData'

describe('getSirenData', () => {
  it('should not call API when SIREN is empty', async () => {
    const siren = ''
    vi.spyOn(api, 'getSirenInfo')

    const response = await getSirenData(siren)

    expect(api.getSirenInfo).not.toHaveBeenCalled()
    expect(response).toStrictEqual({
      values: {
        address: '',
        city: '',
        name: '',
        postalCode: '',
        siren: siren,
        apeCode: '',
      },
    })
  })

  it('should return an error when the SIREN does not exist', async () => {
    const siren = '245474278'
    vi.spyOn(api, 'getSirenInfo').mockRejectedValue(
      new ApiError(
        { method: 'GET', url: 'https://api.gouv.fr/api/v1/sirene/245474278' },
        {
          status: 400,
          statusText: 'Bad Request',
          body: {
            global: ['Le format de ce SIREN ou SIRET est incorrect.'],
          },
          url: 'https://api.gouv.fr/api/v1/sirene/245474278',
          ok: false,
        },
        ''
      )
    )

    try {
      await getSirenData(siren)
    } catch (error) {
      expect(isError(error)).toBeTruthy()
      if (isError(error)) {
        expect(error.message).toBe(
          'Le format de ce SIREN ou SIRET est incorrect.'
        )
      }
    }
  })

  it('should return location values when the SIREN exists', async () => {
    const siren = '445474278'
    vi.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'nom du lieu',
      siren: siren,
      ape_code: '90.03A',
      address: {
        street: '3 rue de la gare',
        city: 'paris',
        postalCode: '75000',
      },
    })

    const response = await getSirenData(siren)

    expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
    expect(api.getSirenInfo).toHaveBeenCalledWith(siren)
    expect(response).toStrictEqual({
      values: {
        address: '3 rue de la gare',
        city: 'paris',
        name: 'nom du lieu',
        postalCode: '75000',
        siren: siren,
        apeCode: '90.03A',
      },
    })
  })
})
