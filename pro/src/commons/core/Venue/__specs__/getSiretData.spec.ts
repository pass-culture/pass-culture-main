import { api } from '@/apiClient/api'
import { isError } from '@/apiClient/helpers'
import { getSiretData } from '@/commons/core/Venue/getSiretData'

describe('getsiretData', () => {
  it('should not call API when SIRET is empty', async () => {
    const siret = ''

    const response = await getSiretData(siret)

    expect(response).toStrictEqual({
      location: null,
      apeCode: null,
      isDiffusible: false,
      name: null,
      siren: null,
      siret: '',
    })
  })

  it('should return an error for wrong siret lengths', async () => {
    try {
      await getSiretData('1')
    } catch (e) {
      expect(isError(e)).toBeTruthy()
      if (isError(e)) {
        expect(e.message).toEqual('SIRET trop court')
      }
    }

    try {
      await getSiretData('123123123123123123')
    } catch (e) {
      expect(isError(e)).toBeTruthy()
      if (isError(e)) {
        expect(e.message).toEqual('SIRET trop long')
      }
    }
  })

  it('should return an error when the SIRET is inactive', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValue({})

    const siret = '11111111111111'

    try {
      await getSiretData(siret)
    } catch (error) {
      expect(isError(error)).toBeTruthy()
      if (isError(error)) {
        expect(error.message).toBe('Impossible de vérifier le SIRET saisi.')
      }
    }
  })
})
