import share from '../share'

describe('reducers | share', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = share(undefined, action)
    const expected = {
      options: null,
      visible: false,
    }

    // then
    expect(updatedState).toStrictEqual(expected)
  })
})
