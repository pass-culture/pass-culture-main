import { getHeaderColor } from '../colors'

describe('getHeaderColor', () => {
  it('should render the corresponding color', () => {
    // given
    const recommendationColor = [0, 0, 0]

    // when
    const result = getHeaderColor(recommendationColor)

    // then
    expect(result).toEqual('black')
  })
  it('should render the corresponding color', () => {
    // given
    const recommendationColor = [56, 45, 78]

    // when
    const result = getHeaderColor(recommendationColor)

    // then
    expect(result).toEqual('hsl(260, 100%, 7.5%)')
  })
  it('should return black by default when array given', () => {
    // when
    const result = getHeaderColor([])

    // then
    expect(result).toEqual('black')
  })
  it('should return black by default when string given', () => {
    // given
    const recommendationColor = 'pink'

    // when
    const result = getHeaderColor(recommendationColor)

    // then
    expect(result).toEqual('black')
  })
})
