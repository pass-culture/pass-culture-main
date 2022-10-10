import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'

import { existsInINSEERegistry } from '../validate'

describe('components | SirenField', () => {
  describe('existsInINSEERegistry', () => {
    it('should call the INSEE API with the formatted SIREN', async () => {
      // given
      jest.spyOn(api, 'getSirenInfo').mockRejectedValue(
        new ApiError(
          {},
          {
            status: 404,
            body: {
              global: ['no results foud'],
            },
          },
          ''
        )
      )
      const siren = '245474278'
      const humanSiren = '245 474 278'

      // when
      await existsInINSEERegistry(humanSiren)

      // then
      expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
      expect(api.getSirenInfo).toHaveBeenCalledWith(
        expect.stringContaining(`${siren}`)
      )
    })

    it('should not return an error message when SIREN exists in INSEE registry', async () => {
      // given
      const siren = '345474278'
      jest.spyOn(api, 'getSirenInfo').mockResolvedValue({
        name: 'nom du lieu',
        siren: '841166096',
        address: {
          street: '3 rue de la gare',
          city: 'paris',
          postalCode: '75000',
        },
      })

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBeUndefined()
    })

    it('should return an error message when the unite_legal has anonymous data', async () => {
      // given
      const siren = '495474278'
      jest.spyOn(api, 'getSirenInfo').mockRejectedValue(
        new ApiError(
          {},
          {
            status: 400,
            body: {
              global: [
                'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles',
              ],
            },
          },
          ''
        )
      )

      // when
      const errorMessage = await existsInINSEERegistry(siren)
      // then
      expect(errorMessage).toBe(
        'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles'
      )
    })

    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siren = '445474278'
      jest.spyOn(api, 'getSirenInfo').mockRejectedValue(
        new ApiError(
          {},
          {
            status: 400,
            body: {
              global: ["Ce SIREN ou SIRET n'existe pas."],
            },
          },
          ''
        )
      )

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBe("Ce SIREN ou SIRET n'existe pas.")
    })

    it('should check once for same SIREN called in INSEE registery', async () => {
      // given
      const siren = '645474278'
      jest.spyOn(api, 'getSirenInfo').mockRejectedValue(
        new ApiError(
          {},
          {
            status: 400,
            body: {
              global: ['no results foud'],
            },
          },
          ''
        )
      )

      // when
      await existsInINSEERegistry(siren)
      await existsInINSEERegistry(siren)

      // then
      expect(api.getSirenInfo).toHaveBeenCalledTimes(1)
      expect(api.getSirenInfo).toHaveBeenCalledWith(
        expect.stringContaining(`${siren}`)
      )
    })
  })
})
