import { getPhoneNumberInputAndCountryCode } from '../getPhoneNumberInputAndCountryCode'

const countryCodeTests: {
  value: string
  expectedInput: string
  expectedCountryCode: string
}[] = [
  {
    value: '06 94 00 01 02',
    expectedInput: '694000102',
    expectedCountryCode: 'GF',
  },
  {
    value: '05 94 00 01 02',
    expectedInput: '594000102',
    expectedCountryCode: 'GF',
  },
  {
    value: '06 92 98 01 01',
    expectedInput: '692980101',
    expectedCountryCode: 'RE',
  },
  {
    value: '02 62 41 83 00',
    expectedInput: '262418300',
    expectedCountryCode: 'RE',
  },
  {
    value: '06 90 41 83 00',
    expectedInput: '690418300',
    expectedCountryCode: 'GP',
  },
  {
    value: '05 90 41 83 00',
    expectedInput: '590418300',
    expectedCountryCode: 'GP',
  },
  {
    value: '06 96 41 83 00',
    expectedInput: '696418300',
    expectedCountryCode: 'MQ',
  },
  {
    value: '05 96 41 83 00',
    expectedInput: '596418300',
    expectedCountryCode: 'MQ',
  },
  {
    value: '',
    expectedInput: '',
    expectedCountryCode: 'FR',
  },
]
describe('getPhoneNumberValues', () => {
  it.each(countryCodeTests)(
    'should should detect $expectedCountryCode country code',
    ({ value, expectedInput, expectedCountryCode }) => {
      const { inputValue, countryCode } =
        getPhoneNumberInputAndCountryCode(value)
      expect(inputValue).toStrictEqual(expectedInput)
      expect(countryCode).toStrictEqual(expectedCountryCode)
    }
  )
})
