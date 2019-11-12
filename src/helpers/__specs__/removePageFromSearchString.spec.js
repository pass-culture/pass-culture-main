import removePageFromSearchString from '../removePageFromSearchString'

describe('src | helpers | removePageFromSearchString', () => {
  describe('removePageFromSearchString', () => {
    it('should remove page when page is at beginning of the string', () => {
      // given
      const searchString = "page=251&type_values=['ThingType.LIVRE_EDITION']"

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe("type_values=['ThingType.LIVRE_EDITION']")
    })

    it('should remove page when page is inside the string', () => {
      // given
      const searchString = "keywords_string=narval&page=12&type_values=['EventType.MUSIQUE']"

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe("keywords_string=narval&type_values=['EventType.MUSIQUE']")
    })

    it('should remove page when page is at end of the string ', () => {
      // given
      const searchString = 'keywords_string=mimi&page=130112'

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe('keywords_string=mimi')
    })
  })
})
