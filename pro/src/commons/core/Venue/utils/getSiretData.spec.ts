import { apiNew } from '@/apiClient/api'
import { isError } from '@/apiClient/helpers'
import {
  checkSiret,
  getSiretData,
} from '@/commons/core/Venue/utils/getSiretData'

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
    vi.spyOn(apiNew, 'getStructureData').mockRejectedValue({})

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

describe('checkSiretRequest', () => {
  it('should throw an error when SIRET is empty', async () => {
    const siret = ''

    try {
      await checkSiret(siret)
    } catch (error) {
      expect(isError(error)).toBeTruthy()
      if (isError(error)) {
        expect(error.message).toEqual('SIRET vide')
      }
    }
  })

  it('should return an error for wrong siret lengths', async () => {
    try {
      await checkSiret('1')
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
    vi.spyOn(apiNew, 'getStructureData').mockRejectedValue({})

    const siret = '11111111111111'

    try {
      await checkSiret(siret)
    } catch (error) {
      expect(isError(error)).toBeTruthy()
      if (isError(error)) {
        expect(error.message).toBe('Impossible de vérifier le SIRET saisi.')
      }
    }
  })

  it('should return an error when the call fails', async () => {
    vi.spyOn(apiNew, 'getStructureData').mockRejectedValueOnce({
      status: 400,
      name: 'ApiError',
      message: 'oh no',
    })

    const siret = '11111111111111'

    try {
      await checkSiret(siret)
    } catch (error) {
      expect(isError(error)).toBeTruthy()
      if (isError(error)) {
        expect(error.message).toBe('oh no')
      }
    }
  })
})
