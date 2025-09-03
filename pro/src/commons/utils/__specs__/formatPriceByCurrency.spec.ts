import { CurrencyEnum } from '@/commons/core/shared/types'
import { formatPriceByCurrency } from '@/commons/utils/formatPriceByCurrency'

const priceByCurrencyTestData = [
  {
    input: 0,
    expected: '0 F',
    currencyFrom: CurrencyEnum.EUR,
    currencyTo: CurrencyEnum.XPF,
  },
  {
    input: 150,
    expected: '17 900 F',
    currencyFrom: CurrencyEnum.EUR,
    currencyTo: CurrencyEnum.XPF,
  },
  {
    input: 15000,
    expected: '1 789 975 F',
    currencyFrom: CurrencyEnum.EUR,
    currencyTo: CurrencyEnum.XPF,
  },
  {
    input: 150,
    expected: '+17 900 F',
    currencyFrom: CurrencyEnum.EUR,
    currencyTo: CurrencyEnum.XPF,
    options: { signDisplay: 'always' } as Intl.NumberFormatOptions,
  },
  {
    input: -50,
    expected: '-5 965 F',
    currencyFrom: CurrencyEnum.EUR,
    currencyTo: CurrencyEnum.XPF,
  },
  {
    input: 200,
    expected: null,
    currencyFrom: CurrencyEnum.XPF,
    currencyTo: CurrencyEnum.EUR,
  },
]

describe('formatPriceByCurrency', () => {
  priceByCurrencyTestData.forEach(
    ({ input, expected, currencyFrom, currencyTo, options }) => {
      it(`should format ${input} from ${currencyFrom} to ${currencyTo} as ${expected}`, () => {
        const call = () =>
          formatPriceByCurrency(
            input,
            { from: currencyFrom, to: currencyTo },
            options
          )
        if (expected === null) {
          const errorInternalMessage = `Conversion from ${currencyFrom} to ${currencyTo} is not supported.`

          expect(call).toThrow(Error)
          expect(call).toThrow(errorInternalMessage)
          return
        } else {
          expect(call()).toEqual(expected)
        }
      })
    }
  )
})
