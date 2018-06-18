import queries from '../queries'
import {PENDING} from '../queries'
import { requestData } from '../data'

describe('src | reducers | queries  ', () => {

  describe('queries', () => {
    let state
    beforeEach(() => {
      state = []
    })

    describe('When action.type is REQUEST_DATA', () => {
      it('should return correct update state', () => {
        // given
        const method = 'POST'
        const path = 'http://fakeUrl.com'
        const config = {
          key: 'fakeKey',
          requestId: 'fakeRequestId'
        }
        const action = requestData(method, path, config)

        // when
        const queriesReducer = queries(state, action,)
        const expected = [
          {
          id: 'fakeRequestId',
          key: 'fakeKey',
          path: path,
          status: PENDING
        }
      ]
        // then
        expect(queriesReducer).toEqual(expected)
      })
    })

    describe('When action.type is REQUEST_DATA', () => {
      it('should return correct update state', () => {
        // given
        const method = 'POST'
        const path = 'http://fakeUrl.com'
        const config = {
          key: 'fakeKey',
          requestId: 'fakeRequestId'
        }
        const action = requestData(method, path, config)

        // when
        const queriesReducer = queries(state, action,)
        const expected = [
          {
          id: 'fakeRequestId',
          key: 'fakeKey',
          path: path,
          status: PENDING
        }
      ]
        // then
        expect(queriesReducer).toEqual(expected)
      })
    })
  })
})
