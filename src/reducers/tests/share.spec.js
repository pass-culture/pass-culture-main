import { share, closeSharePopin, openSharePopin } from '../share'

describe('src | reducers | share  ', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = share(undefined, action)
    const expected = {
      options: false,
      visible: false,
    }

    // then
    expect(updatedState).toStrictEqual(expected)
  })
})

describe('src | reducers | action | openSharePopin', () => {
  it('should return correct action type', () => {
    // when
    const action = openSharePopin()
    const expected = {
      type: 'TOGGLE_SHARE_POPIN',
    }

    // then
    expect(action).toMatchObject(expected)
  })
})

describe('src | reducers | action | closeSharePopin', () => {
  it('should return correct action type', () => {
    // when
    const action = closeSharePopin()
    const expected = {
      options: false,
      type: 'TOGGLE_SHARE_POPIN',
    }

    // then
    expect(action).toMatchObject(expected)
  })
})
