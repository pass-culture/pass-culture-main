import { normalizeStrForSearch } from '../normalizeStrForSearch'

describe('normalizeStrForSearch', () => {
  it('should return the same string', () => {
    expect(normalizeStrForSearch('hello')).toBe('hello')
  })

  it('should handle empty string', () => {
    expect(normalizeStrForSearch('')).toBe('')
  })

  it('should handle string with only whitespace', () => {
    expect(normalizeStrForSearch('   ')).toBe('')
  })

  it('should deduplicate spaces and trim leading/trailing whitespaces', () => {
    expect(normalizeStrForSearch('  hello  pass culture  ')).toBe(
      'hello pass culture'
    )
  })

  it('should strip accents', () => {
    expect(normalizeStrForSearch('Éléphant français naïf')).toBe(
      'elephant francais naif'
    )
  })

  it('should strip punctuation', () => {
    expect(normalizeStrForSearch('La dictée virgule, point final.')).toBe(
      'la dictee virgule point final'
    )
  })
})
