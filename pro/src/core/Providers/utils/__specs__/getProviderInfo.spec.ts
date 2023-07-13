import { getProviderInfo } from 'core/Providers'

describe('getProviderInfo', () => {
  it('should return provider information which id match lowercase name', () => {
    expect(getProviderInfo('FNAC')).toStrictEqual({
      id: 'fnac',
      logo: expect.any(String),
      name: 'Fnac',
      synchronizedOfferMessage: 'Offre synchronisée avec Fnac',
    })
  })

  it('should return provider information which id match beginning of name', () => {
    expect(getProviderInfo('titelive stocks')).toStrictEqual({
      id: 'titelive',
      logo: expect.any(String),
      name: 'Tite Live',
      synchronizedOfferMessage: 'Offre synchronisée avec Tite Live',
    })
  })
  it('should return provider information if not known by the front', () => {
    expect(getProviderInfo('Mon provider à moi !')).toStrictEqual({
      id: 'mon provider à moi !',
      logo: expect.any(String),
      name: 'Mon provider à moi !',
      synchronizedOfferMessage: 'Offre synchronisée avec Mon provider à moi !',
    })
  })
})
