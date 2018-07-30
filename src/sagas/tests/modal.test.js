import { takeEvery, fork } from 'redux-saga/effects'

import {
  fromWatchCloseModalAction,
  fromWatchShowModalAction,
  watchModalActions,
} from '../modal'
import { CLOSE_MODAL, SHOW_MODAL } from '../../reducers/modal'

describe('src | sagas | modal', () => {
  describe('fromWatchCloseModalAction', () => {
    // when
    fromWatchCloseModalAction()

    // then
    expect(document.body.style.overflow).toEqual('auto')
  })

  describe('fromWatchShowModalAction', () => {
    // when
    fromWatchShowModalAction()

    // then
    expect(document.body.style.overflow).toEqual('hidden')
  })

  describe('watchModalActions', () => {
    it('should do call fromWatchCloseModalAction with CLOSE_MODAL action', () => {
      // given
      const generator = watchModalActions()

      // when
      const descriptor = generator.next().value
      const expected = JSON.stringify(
        fork(takeEvery, CLOSE_MODAL, fromWatchCloseModalAction)
      )

      // then
      expect(JSON.stringify(descriptor)).toEqual(expected)
    })
  })
  it('should do call fromWatchShowModalAction with SHOW_MODAL action', () => {
    // given
    const generator = watchModalActions()
    generator.next()

    // when
    const descriptor = generator.next().value
    const expected = JSON.stringify(
      fork(takeEvery, SHOW_MODAL, fromWatchShowModalAction)
    )

    // then
    expect(JSON.stringify(descriptor)).toBe(expected)
  })
})
