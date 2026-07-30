import { removeQuotes } from '@/commons/utils/removeQuotes'

describe('removeQuotes', () => {
  it.each([
    {
      description: 'double quotes',
      original: 'Place de la "Belle Épine"',
      expected: 'Place de la Belle Épine',
    },
    {
      description: 'french quotation marks',
      original: 'Place de la « Belle Épine »',
      expected: 'Place de la Belle Épine',
    },
    {
      description: 'english quotation marks',
      original: 'Place de la “Belle Épine“',
      expected: 'Place de la Belle Épine',
    },
  ])(
    'should trim and remove $description from a string',
    ({ original, expected }) => {
      expect(removeQuotes(original)).toBe(expected)
    }
  )
})
