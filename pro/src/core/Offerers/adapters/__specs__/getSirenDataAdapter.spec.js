import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { unhumanizeSiren } from 'core/Offerers/utils'

import getSirenDataAdapter from '../getSirenDataAdapter'

describe('getSirenDataAdapter', () => {
  describe('when the SIREN is invalidate', () => {
    it('should not call API when SIREN is empty', async () => {
      // given
      const siren = ''
      vi.spyOn(api, 'getSirenInfo')

      // when
      const response = await getSirenDataAdapter(siren)

      // then
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
  })

  describe('when the SIREN does not exist', () => {
    it('test invalid siret response', async () => {
      // given
      const siren = '245474278'
      vi.spyOn(api, 'getSirenInfo').mockRejectedValue(
        new ApiError(
          {},
          {
            status: 400,
            body: {
              global: ['Le format de ce SIREN ou SIRET est incorrect.'],
            },
          },
          ''
        )
      )

      // when
      const response = await getSirenDataAdapter(siren)

      // then
      expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Le format de ce SIREN ou SIRET est incorrect.'
      )
      expect(response.payload).toStrictEqual({})
    })
  })

  describe('when the SIREN exists', () => {
    it('should return location values', async () => {
      // given
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

      // when
      const response = await getSirenDataAdapter(siren)

      // then
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
})
