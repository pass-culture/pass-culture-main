import { RootState } from 'store/reducers'
import { initialState } from 'store/reducers/notificationReducer'

import { notificationSelector } from '../notificationSelector'

describe('notificationSelector', () => {
  it('should return empty state when no notification is stored', () => {
    const state = {
      notification: initialState,
    } as RootState

    const notification = notificationSelector(state)

    expect(notification).toStrictEqual(null)
  })

  it('should return notification details when notification is stored', () => {
    const state = {
      notification: {
        ...initialState,
        notification: { type: 'success', text: 'My success message' },
      },
    } as RootState

    const notification = notificationSelector(state)

    expect(notification).toStrictEqual(state.notification.notification)
  })
})
