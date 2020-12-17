import { PROVIDER_ICONS } from '../../../../utils/providers'
import { getProviderInfo } from '../getProviderInfo'

describe('src | getProviderInfo', () => {
  it('should return provider information which id match lowercase name', () => {
    // given
    const providerName = 'FNAC'

    // when
    const providerInfo = getProviderInfo(providerName)

    // then
    expect(providerInfo).toStrictEqual({
      id: 'fnac',
      icon: PROVIDER_ICONS['FnacStocks'],
      name: 'Fnac',
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
      icon: PROVIDER_ICONS['TiteLiveStocks'],
      name: 'Tite Live',
    })
  })
})
