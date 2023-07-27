import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { unhumanizeSiren } from 'core/Offerers/utils'

import getSirenDataAdapter from '../getSirenDataAdapter'

describe('getSirenDataAdapter', () => {
  it('should not call API when SIREN is empty', async () => {
    const siren = ''
    vi.spyOn(api, 'getSirenInfo')

    const response = await getSirenDataAdapter(siren)

    expect(api.getSirenInfo).not.toHaveBeenCalled()
    expect(response.payload).toStrictEqual({
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

    const response = await getSirenDataAdapter(siren)

    expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Le format de ce SIREN ou SIRET est incorrect.'
    )
    expect(response.payload).toStrictEqual({})
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

    const response = await getSirenDataAdapter(siren)

    expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
    expect(api.getSirenInfo).toHaveBeenCalledWith(siren)
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      `Informations récupéré avec success pour le SIREN: ${unhumanizeSiren(
        siren
      )}`
    )
    expect(response.payload).toStrictEqual({
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
