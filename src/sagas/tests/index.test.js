import { all } from 'redux-saga/effects'

import rootSaga from '../index'
import {
  watchDataActions,
  watchErrorsActions,
} from 'pass-culture-shared'

import { watchModalActions } from '../modal'
import { watchUserActions } from '../user'

describe('src | sagas | index', () => {

  describe('rootSaga', () => {
    it('should do call watchModalActions, watchDataActions and watchUserActions', () => {
      // given
      const generator = rootSaga()

      // when
      const descriptor = generator.next().value
      const expected = JSON.stringify(all([watchModalActions(), watchDataActions(), watchUserActions(), watchErrorsActions()]))

      //
      // then
      expect(JSON.stringify(descriptor)).toEqual(expected)
    })
  })

})
