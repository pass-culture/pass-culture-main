import { mapSizeToProps } from '../DeckContainer'

describe('src | components | pages | discovery | deck | DeckContainer', () => {
  describe('mapSizeToProps', () => {
    it('should return an object containing given height and width inferior to 500', () => {
      // given
      const dimensions = {
        height: 200,
        width: 100,
      }
      const expectedResult = { height: 200, width: 100 }

      // when
      const result = mapSizeToProps(dimensions)

      // then
      expect(result).toStrictEqual(expectedResult)
    })

    it('should return an object containing height and width equal to 500 when width > 500', () => {
      // given
      const dimensions = {
        height: 200,
        width: 800,
      }
      const expectedResult = { height: 200, width: 500 }

      // when
      const result = mapSizeToProps(dimensions)

      // then
      expect(result).toStrictEqual(expectedResult)
    })
  })
})
