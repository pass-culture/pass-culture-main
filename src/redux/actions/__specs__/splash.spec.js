import { closeSplash, showSplash } from '../splash'

describe('actions | showSplash', () => {
  it('should return correct action type', () => {
    // when
    const action = closeSplash()
    const expected = {
      type: 'CLOSE_SPLASH',
    }

    // then
    expect(action).toMatchObject(expected)
  })

  it('should return correct action type (réécrire)', () => {
    // when
    const action = showSplash()
    const expected = {
      type: 'SHOW_SPLASH',
    }

    // then
    expect(action).toMatchObject(expected)
  })
})
