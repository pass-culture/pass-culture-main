import type { CurrencyCode } from '@/commons/core/shared/types'
import { formatPrice } from '@/commons/utils/formatPrice'

type TestPriceData = {
  price: number
  options?: Intl.NumberFormatOptions
  currency?: CurrencyCode
  expected: string
}

const testPriceData: TestPriceData[] = [
  { price: 12, expected: '12,00\xa0€' },
  { price: 12000, expected: '12\u202f000,00\xa0€' },
  { price: 10, options: { maximumFractionDigits: 0 }, expected: '10\xa0€' },
  { price: 150, currency: 'XPF', expected: '150\xa0F' },
  { price: 15000, currency: 'XPF', expected: '15\u202f000\xa0F' },
  {
    price: 15000,
    currency: 'XPF',
    options: { signDisplay: 'always' },
    expected: '+15\u202f000\xa0F',
  },
  {
    price: -15000,
    currency: 'XPF',
    options: { signDisplay: 'always' },
    expected: '-15\u202f000\xa0F',
  },
]

describe('formatPrice', () => {
  testPriceData.forEach(({ price, options, currency, expected }) => {
    it(`should format ${price} with options ${JSON.stringify(options)}`, () => {
      const formattedPrice = formatPrice(price, options, currency)
      expect(formattedPrice).toBe(expected)
    })
  })
})
