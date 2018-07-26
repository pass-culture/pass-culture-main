import { all } from 'redux-saga/effects'

import rootSaga from '../index'
import { watchModalActions } from '../modal'
import { watchDataActions } from '../data'
import { watchUserActions } from '../user'

describe('src | sagas | index', () => {

  describe('rootSaga', () => {
    it('should do call watchModalActions, watchDataActions and watchUserActions', () => {
      // given
      const generator = rootSaga()

      // when
      const descriptor = generator.next().value
      const expected = JSON.stringify(all([watchModalActions(), watchDataActions(), watchUserActions()]))

      //
      // then
      expect(JSON.stringify(descriptor)).toEqual(expected)
    })
  })

})
