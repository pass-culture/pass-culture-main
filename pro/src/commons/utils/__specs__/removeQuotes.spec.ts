import { removeQuotes } from '@/commons/utils/removeQuotes'

describe('removeQuotes', () => {
  it('should trim and removes double quotes " " from a string', () => {
    const original = 'Place de la "Belle Épine"'
    const expected = 'Place de la Belle Épine'

    expect(removeQuotes(original)).toBe(expected)
  })

  it('should trim and removes french quotation marks « » from a string', () => {
    const original = 'Place de la « Belle Épine »'
    const expected = 'Place de la Belle Épine'

    expect(removeQuotes(original)).toBe(expected)
  })

  it('should trim and removes english quotation marks “ ” from a string', () => {
    const original = 'Place de la “Belle Épine”'
    const expected = 'Place de la Belle Épine'

    expect(removeQuotes(original)).toBe(expected)
  })
})
