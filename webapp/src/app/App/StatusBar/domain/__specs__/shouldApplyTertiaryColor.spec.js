import { shouldApplyTertiaryColor } from '../shouldApplyTertiaryColor'

describe('should status bar be colored in tertiary color', () => {
  describe('when user is on a page without a purple header', () => {
    it('should return false', () => {
      // given
      const offerPage = '/offre/YTRE/FD'

      // when
      const result = shouldApplyTertiaryColor(offerPage)

      // then
      expect(result).toBe(false)
    })
  })

  describe('when user is on a page with a purple header', () => {
    it('should return true', () => {
      // given
      const pathsWithTertiaryColor = ['/accueil']

      pathsWithTertiaryColor.forEach(path => {
        // when
        const result = shouldApplyTertiaryColor(path)
        // then
        expect(result).toBe(true)
      })
    })
  })
})
