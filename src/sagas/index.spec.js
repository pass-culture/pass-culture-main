import { all } from 'redux-saga/effects'
import { watchModalActions } from 'redux-react-modals'
import { watchDataActions } from 'redux-saga-data'

import rootSaga from './index'
import { API_URL } from '../utils/config'

describe('src | components | sagas', () => {
  describe('rootSaga', () => {
    const defaultSaga = rootSaga()

    it('should yield all shared sagas', () => {
      // given
      const allDescriptor = defaultSaga.next().value

      // when
      all([watchModalActions(), watchDataActions({ rootUrl: API_URL })])

      // then
      expect(allDescriptor.ALL[0]).toStrictEqual(watchModalActions())
    })
  })
})
