import { getPhoneNumberInputAndCountryCode } from '../getPhoneNumberInputAndCountryCode'

describe('getPhoneNumberValues', () => {
  it('should detect GF country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('06 94 00 01 02')
    expect(inputValue).toStrictEqual('694000102')
    expect(countryCode).toStrictEqual('GF')
  })

  it('should detect RE country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('06 39 98 01 01')
    expect(inputValue).toStrictEqual('639980101')
    expect(countryCode).toStrictEqual('RE')
  })

  it('should return default value', () => {
    const { inputValue, countryCode } = getPhoneNumberInputAndCountryCode('')
    expect(inputValue).toStrictEqual('')
    expect(countryCode).toStrictEqual('FR')
  })
})
