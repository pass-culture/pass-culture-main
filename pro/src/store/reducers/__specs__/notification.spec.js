import {
  closeNotification,
  notificationReducer,
  showNotification,
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
      expect(state).toBeNull()
    })
  })

  describe('when action.type is SHOW_NOTIFICATION', () => {
    it('should return correct update state', () => {
      // given
      const notificationMessage = {
        text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
        type: 'success',
      }
      const action = showNotification(notificationMessage)

      // when
      const state = notificationReducer(initialState, action)

      // then
      expect(state).toStrictEqual({ ...notificationMessage })
    })
  })
})
