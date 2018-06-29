import notification,
{
  closeNotification,
  showNotification
} from '../notification'

import { CLOSE_NOTIFICATION, SHOW_NOTIFICATION } from '../notification'

jest.mock('../../utils/dom', () => ({
  scrollIt: () => {
  },
}))

describe('src | reducers | notification  ', () => {

  let initialState
  beforeEach(() => {
    initialState = []
  })

  describe('When action.type is CLOSE_NOTIFICATION', () => {

    it('should return correct update state', () => {
      // given
      const action = closeNotification()

      // when
      const notificationReducer = notification(initialState, action)

      // then
      expect(notificationReducer).toEqual(null)
    })
  })

  describe('When action.type is SHOW_NOTIFICATION', () => {

    it('should return correct update state', () => {
      // given
      const notificationMessage = {
        text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
        type: 'success'
      }
      const action = showNotification(notificationMessage)

      // when
      const notificationReducer = notification(initialState, action)

      // then
      expect(notificationReducer).toEqual(notificationMessage)
    })
  })

})

describe('src | actions  ', () => {

  const notification = {
    text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
    type: 'success'
  }

  describe('closeNotification  ', () => {
    const expected = {
      type: CLOSE_NOTIFICATION
    }
    expect(closeNotification(notification)).toEqual(expected)
  })

  describe('showNotification  ', () => {
    const expected = {
      type: SHOW_NOTIFICATION,
      notification
    }
    expect(showNotification(notification)).toEqual(expected)
  })

})
