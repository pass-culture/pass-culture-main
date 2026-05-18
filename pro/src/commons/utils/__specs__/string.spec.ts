import { removeWhitespaces, truncateAtWord } from '../string'

describe('removeWhitespaces', () => {
  it('removes every whitespace character from the string', () => {
    expect(removeWhitespaces('  hello  world\t\n')).toBe('helloworld')
  })

  it('returns the input unchanged when it is empty', () => {
    expect(removeWhitespaces('')).toBe('')
  })
})

describe('truncateAtWord', () => {
  it('returns the text unchanged when it is shorter than the limit', () => {
    expect(truncateAtWord('short text', 50)).toBe('short text')
  })

  it('cuts at the last space when the limit splits a word', () => {
    expect(truncateAtWord('Lorem ipsum dolor sit amet', 15)).toBe(
      'Lorem ipsum...'
    )
  })

  it('does not back off to a previous space when the cut lands on a word boundary', () => {
    expect(truncateAtWord('Lorem ipsum dolor', 11)).toBe('Lorem ipsum...')
  })

  it('uses the provided ending suffix', () => {
    expect(
      truncateAtWord('Lorem ipsum dolor sit amet', 15, ' Afficher plus...')
    ).toBe('Lorem ipsum Afficher plus...')
  })

  it('falls back to a hard cut when no space is available before the limit', () => {
    expect(truncateAtWord('Loremipsumdolor', 5)).toBe('Lorem...')
  })
})
