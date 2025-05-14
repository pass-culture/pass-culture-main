import { api } from 'apiClient/api'
import { isError } from 'apiClient/helpers'
import { getSiretData } from 'commons/core/Venue/getSiretData'

describe('getsiretData', () => {
  it('should not call API when SIRET is empty', async () => {
    const siret = ''
    vi.spyOn(api, 'getSiretInfo')

    const response = await getSiretData(siret)

    expect(api.getSiretInfo).not.toHaveBeenCalled()
    expect(response).toStrictEqual({
      values: {
        address: '',
        city: '',
        latitude: null,
        longitude: null,
        name: '',
        postalCode: '',
        inseeCode: '',
        siret: '',
        apeCode: '',
        legalCategoryCode: '',
        banId: '',
      },
    })
  })

  it('should return an error for wrong siret lengths', async () => {
    vi.spyOn(api, 'getSiretInfo')

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
    const siret = '11111111111111'
    vi.spyOn(api, 'getSiretInfo').mockResolvedValueOnce({
      active: false,
      address: {
        city: '',
        postalCode: '',
        street: '',
      },
      ape_code: '',
      legal_category_code: '',
      name: '',
      siret: siret,
    })

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
