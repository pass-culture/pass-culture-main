import { getPhoneNumberInputAndCountryCode } from '../getPhoneNumberInputAndCountryCode'

describe('getPhoneNumberValues', () => {
  it('should detect GF country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('06 94 00 01 02')
    expect(inputValue).toStrictEqual('694000102')
    expect(countryCode).toStrictEqual('GF')
  })

  it('should detect GF fix country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('05 94 00 01 02')
    expect(inputValue).toStrictEqual('594000102')
    expect(countryCode).toStrictEqual('GF')
  })

  it('should detect RE country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('692 98 01 01')
    expect(inputValue).toStrictEqual('692980101')
    expect(countryCode).toStrictEqual('RE')
  })

  it('should detect RE fix country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('02 62 41 83 00')
    expect(inputValue).toStrictEqual('262418300')
    expect(countryCode).toStrictEqual('RE')
  })

  it('should detect GP country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('06 90 41 83 00')
    expect(inputValue).toStrictEqual('690418300')
    expect(countryCode).toStrictEqual('GP')
  })

  it('should detect GP fix country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('05 90 41 83 00')
    expect(inputValue).toStrictEqual('590418300')
    expect(countryCode).toStrictEqual('GP')
  })

  it('should detect MQ country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('06 96 41 83 00')
    expect(inputValue).toStrictEqual('696418300')
    expect(countryCode).toStrictEqual('MQ')
  })

  it('should detect MQ fix country code', () => {
    const { inputValue, countryCode } =
      getPhoneNumberInputAndCountryCode('05 96 41 83 00')
    expect(inputValue).toStrictEqual('596418300')
    expect(countryCode).toStrictEqual('MQ')
  })

  it('should return default value', () => {
    const { inputValue, countryCode } = getPhoneNumberInputAndCountryCode('')
    expect(inputValue).toStrictEqual('')
    expect(countryCode).toStrictEqual('FR')
  })
})
