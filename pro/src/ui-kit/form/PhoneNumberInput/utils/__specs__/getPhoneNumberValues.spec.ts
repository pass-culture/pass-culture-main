import { getPhoneNumberValues } from '../getPhoneNumberValues'

describe('getPhoneNumberValues', () => {
  it('should detect GF country code', () => {
    const { inputValue, countryCode } = getPhoneNumberValues('06 94 00 01 02')
    expect(inputValue).toStrictEqual('694 00 01 02')
    expect(countryCode).toStrictEqual('GF')
  })

  it('should detect FR country code', () => {
    const { inputValue, countryCode } = getPhoneNumberValues('06 39 98 01 01')
    expect(inputValue).toStrictEqual('639980101')
    expect(countryCode).toStrictEqual('FR')
  })
})
