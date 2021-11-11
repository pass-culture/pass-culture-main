import splash from '../splash'
import { CLOSE_SPLASH, SHOW_SPLASH } from '../../actions/splash'

describe('src | reducers | splash', () => {
  it('should return the initial state by default', () => {
    // given
    const initialState = {
      closeTimeout: 1500,
      isActive: true,
    }
    const action = {}

    // when
    const updatedState = splash(undefined, action)

    // then
    expect(updatedState).toStrictEqual(initialState)
  })

  it('should set state when action is CLOSE_SPLASH', () => {
    // given
    const state = {}
    const action = { type: CLOSE_SPLASH }

    // when
    const updatedState = splash(state, action)
    const expected = { isActive: false }

    // then
    expect(updatedState).toStrictEqual(expected)
  })

  it('should set state when action is SHOW_SPLASH', () => {
    // given
    const state = {}
    const action = { type: SHOW_SPLASH }

    // when
    const updatedState = splash(state, action)
    const expected = { isActive: true }

    // then
    expect(updatedState).toStrictEqual(expected)
  })
})
