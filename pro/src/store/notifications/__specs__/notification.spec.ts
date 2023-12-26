import { NotificationTypeEnum } from 'hooks/useNotification'

import {
  closeNotification,
  notificationsReducer,
  showNotification,
  initialState as notificationInitialState,
  NotificationState,
} from '../reducer'

describe('notificationsReducer', () => {
  let initialState: NotificationState
  beforeEach(() => {
    initialState = notificationInitialState
  })

  it('should remove the notification when closing it', () => {
    const action = closeNotification()

    const state = notificationsReducer(initialState, action)

    expect(state.notification).toBeNull()
  })

  it('should add a notification when receiving it', () => {
    const notificationMessage = {
      text: 'Votre structure a bien été enregistrée, elle est en cours de validation.',
      type: NotificationTypeEnum.SUCCESS,
    }
    const action = showNotification(notificationMessage)

    const state = notificationsReducer(initialState, action)

    expect(state.notification).toStrictEqual(notificationMessage)
  })
})
