import { unhumanizeSiren } from 'core/Offerers/utils'

import getSirenDataAdapter from '../getSirenDataAdapter'

describe('getSirenDataAdapter', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })
  describe('when the SIREN is invalidate', () => {
    it('should not call API when SIREN is empty', async () => {
      // given
      const siren = ''

      // when
      const response = await getSirenDataAdapter(siren)

      // then
      expect(fetch).not.toHaveBeenCalled()
      expect(response.payload).toStrictEqual({
        values: {
          address: '',
          city: '',
          name: '',
          postalCode: '',
          siren: siren,
        },
      })
    })
  })

  describe('when the SIREN does not exist', () => {
    it('test invalid siret response', async () => {
      // given
      const siren = '245474278'
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: ['Le format de ce SIREN ou SIRET est incorrect.'],
          }),
      })

      // when
      const response = await getSirenDataAdapter(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
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
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            name: 'nom du lieu',
            siren: siren,
            address: {
              street: '3 rue de la gare',
              city: 'paris',
              postalCode: '75000',
            },
          }),
      })

      // when
      const response = await getSirenDataAdapter(siren)
      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toContain(`/sirene/siren/${siren}`)
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
        },
      })
    })
  })
})
