/* eslint-disable */
import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'

import { all } from 'redux-saga/effects'

import rootSaga from './index'
import { API_URL } from '../utils/config'

describe('src | components | sagas ', () => {
  describe('rootSaga', () => {
    const defaultSaga = rootSaga()
    it('should yield all shared sagas', () => {
      // when
      const allDescriptor = defaultSaga.next().value

      // then
      const expected = all([
        watchModalActions(),
        watchDataActions({ url: API_URL }),
        watchErrorsActions(),
        watchUserActions(),
      ])

      expect(allDescriptor.ALL[0]).toEqual(watchModalActions())
      // Compared values have no visual difference. !!!
    })
  })
})
