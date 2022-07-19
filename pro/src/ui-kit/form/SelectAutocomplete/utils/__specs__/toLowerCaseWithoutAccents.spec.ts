import { toLowerCaseWithoutAccents } from '../toLowerCaseWithoutAccents'

describe('toLowerCaseWithoutAccents', () => {
  it('should format value', () => {
    expect(
      toLowerCaseWithoutAccents('Le théâtre de Gaël, ça va être cool')
    ).toStrictEqual('le theatre de gael, ca va etre cool')
  })

  it('should do nothing', () => {
    expect(
      toLowerCaseWithoutAccents('une string sans accents ni majuscules')
    ).toStrictEqual('une string sans accents ni majuscules')
    expect(toLowerCaseWithoutAccents('')).toStrictEqual('')
  })
})
