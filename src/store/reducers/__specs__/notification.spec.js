import {
  closeNotification,
  notificationReducer,
  showNotificationV1,
  showNotificationV2,
} from 'store/reducers/notificationReducer'

describe('src | reducers | notification', () => {
  let initialState
  beforeEach(() => {
    initialState = []
  })

  describe('when action.type is CLOSE_NOTIFICATION', () => {
    it('should return correct update state', () => {
      // given
      const action = closeNotification()

      // when
      const state = notificationReducer(initialState, action)

      // then
      expect(state).toStrictEqual({})
    })
  })

  describe('when action.type is SHOW_NOTIFICATION_V1', () => {
    it('should return correct update state', () => {
      // given
      const notificationMessage = {
        text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
        type: 'success',
      }
      const action = showNotificationV1(notificationMessage)

      // when
      const state = notificationReducer(initialState, action)

      // then
      expect(state).toStrictEqual({ version: 1, ...notificationMessage })
    })
  })

  describe('when action.type is SHOW_NOTIFICATION_V2', () => {
    it('should return correct update state', () => {
      // given
      const notificationMessage = {
        text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
        type: 'success',
      }
      const action = showNotificationV2(notificationMessage)

      // when
      const state = notificationReducer(initialState, action)

      // then
      expect(state).toStrictEqual({ version: 2, ...notificationMessage })
    })
  })
})
