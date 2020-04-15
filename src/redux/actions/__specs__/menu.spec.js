import { toggleMainMenu } from '../menu'

describe('actions | toggleMainMenu', () => {
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
