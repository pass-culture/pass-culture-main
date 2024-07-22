import { getProviderInfo } from '../getProviderInfo'

describe('getProviderInfo', () => {
  it('should return provider information which id match lowercase name', () => {
    expect(getProviderInfo('FNAC')).toStrictEqual({
      id: 'fnac',
      logo: expect.any(String),
      name: 'FNAC',
      synchronizedOfferMessage: 'Offre synchronisée avec FNAC',
    })
  })

  it('should return provider information which id match beginning of name', () => {
    expect(getProviderInfo('Titelive stocks')).toStrictEqual({
      id: 'titelive stocks',
      logo: expect.any(String),
      name: 'Titelive stocks',
      synchronizedOfferMessage: 'Offre synchronisée avec Titelive stocks',
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
