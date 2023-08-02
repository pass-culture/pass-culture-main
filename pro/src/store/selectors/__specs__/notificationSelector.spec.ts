import { RootState } from 'store/reducers'
import { notificationInitialState } from 'store/reducers/notificationReducer'

import { notificationSelector } from '../notificationSelector'

describe('notificationSelector', () => {
  it('should return empty state when no notification is stored', () => {
    const state = {
      notification: notificationInitialState,
    } as RootState

    const notification = notificationSelector(state)

    expect(notification).toStrictEqual(null)
  })

  it('should return notification details when notification is stored', () => {
    const state = {
      notification: {
        ...notificationInitialState,
        notification: { type: 'success', text: 'My success message' },
      },
    } as RootState

    const notification = notificationSelector(state)

    expect(notification).toStrictEqual(state.notification.notification)
  })
})
