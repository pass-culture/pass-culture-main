import { isAllocineProvider, isCinemaProvider } from '../utils'

describe('providers utils', () => {
  describe('isAllocineProvider', () => {
    it('returns true for accented Allocine name', () => {
      expect(isAllocineProvider({ name: 'Allociné' })).toBe(true)
    })

    it('returns true for unicode escaped/normalized variant', () => {
      expect(isAllocineProvider({ name: 'Allocin\u00e9' })).toBe(true)
    })

    it('returns true with extra spaces and mixed case', () => {
      expect(isAllocineProvider({ name: '  ALLOCINÉ  ' })).toBe(true)
    })

    it('returns false for unknown provider', () => {
      expect(isAllocineProvider({ name: 'Boost' })).toBe(false)
    })
  })

  describe('isCinemaProvider', () => {
    it('returns true for cinema providers regardless of case/accents', () => {
      expect(isCinemaProvider({ name: 'CINÉ OFFICE' })).toBe(true)
      expect(isCinemaProvider({ name: 'boost' })).toBe(true)
    })

    it('returns false for unknown provider', () => {
      expect(isCinemaProvider({ name: 'Unknown provider' })).toBe(false)
    })
  })
})
