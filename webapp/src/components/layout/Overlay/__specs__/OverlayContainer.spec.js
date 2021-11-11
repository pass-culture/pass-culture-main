import { mapStateToProps } from '../OverlayContainer'

describe('src | components | layout | Overlay | OverlayContainer', () => {
  it('should return good props', () => {
    // given
    let state = {
      overlay: true,
      share: { visible: false },
    }

    // when
    const result = mapStateToProps(state)

    // then
    const expected = {
      isVisible: true,
    }
    expect(result).toStrictEqual(expected)
  })
})
