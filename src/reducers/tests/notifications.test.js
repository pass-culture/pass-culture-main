import notification from '../notification'
import {PENDING} from '../notification'
import { requestData } from '../data'

describe('src | reducers | notification  ', () => {

  describe('notification', () => {
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
        const notificationReducer = notification(state, action)
        const expected = [
          {
          "id": "fakeRequestId",
          "key": "fakeKey",
          "path": path,
          status: PENDING
        }
      ]
        // then
        expect(notificationReducer).toEqual(expected)
      })
    })
  })
})
