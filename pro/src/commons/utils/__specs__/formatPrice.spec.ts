import { formatPrice } from '@/commons/utils/formatPrice'

describe('formatPrice', () => {
  it('should add the currency sign to a price', () => {
    expect(formatPrice(12)).toEqual('12,00\xa0€')
  })

  it('should add spaces between groups of digits when the price is above 1000', () => {
    //  Intl NumberFormat use small non-breaking space (\u202f) for thousand separator and normal non-breaking space beforece currency (\xa0)
    expect(formatPrice(12000)).toEqual('12\u202f000,00\xa0€')
  })

  it('should specify formatting options such as the number of fraction digits', () => {
    expect(formatPrice(10, { maximumFractionDigits: 0 })).toEqual('10\xa0€')
  })
})
