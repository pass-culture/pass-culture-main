import menu from '../menu'

describe('src | reducers | menu', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = menu(undefined, action)

    // then
    expect(updatedState).toStrictEqual(false)
  })
})
