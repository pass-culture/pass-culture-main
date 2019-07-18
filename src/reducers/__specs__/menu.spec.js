import menu, { toggleMainMenu } from '../menu'

describe('src | reducers | menu  ', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = menu(undefined, action)

    // then
    expect(updatedState).toStrictEqual(false)
  })
})

describe('src | reducers | action | toggleMainMenu', () => {
  it('should return correct action type', () => {
    // when
    const action = toggleMainMenu({
      type: 'TOGGLE_MAIN_MENU',
    })
    const expected = {
      type: 'TOGGLE_MAIN_MENU',
    }

    // then
    expect(action).toMatchObject(expected)
  })
})
