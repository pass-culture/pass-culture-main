import { getProviderInfo } from 'core/Providers'

describe('src | getProviderInfo', () => {
  it('should return provider information which id match lowercase name', () => {
    // given
    const providerName = 'FNAC'

    // when
    const providerInfo = getProviderInfo(providerName)

    // then
    expect(providerInfo).toStrictEqual({
      id: 'fnac',
      icon: 'logo-fnac',
      name: 'Fnac',
      synchronizedOfferMessage: 'Offre synchronisée avec Fnac',
    })
  })

  it('should return provider information which id match beginning of name', () => {
    // given
    const providerName = 'titelive stocks'

    // when
    const providerInfo = getProviderInfo(providerName)

    // then
    expect(providerInfo).toStrictEqual({
      id: 'titelive',
      icon: 'logo-titeLive',
      name: 'Tite Live',
      synchronizedOfferMessage: 'Offre synchronisée avec Tite Live',
    })
  })
})
