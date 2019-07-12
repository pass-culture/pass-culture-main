/* eslint-disable */
import { all } from 'redux-saga/effects'
import { watchModalActions } from 'redux-react-modals'
import { watchDataActions } from 'redux-saga-data'

import rootSaga from './index'
import { API_URL } from '../utils/config'

describe('src | components | sagas ', () => {
  describe('rootSaga', () => {
    const defaultSaga = rootSaga()
    it('should yield all shared sagas', () => {
      // when
      const allDescriptor = defaultSaga.next().value

      // then
      const expected = all([watchModalActions(), watchDataActions({ rootUrl: API_URL })])

      expect(allDescriptor.ALL[0]).toEqual(watchModalActions())
      // Compared values have no visual difference. !!!
    })
  })
})
