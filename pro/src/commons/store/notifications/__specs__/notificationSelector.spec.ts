import { RootState } from '@/commons/store/rootReducer'

import { initialState } from '../reducer'
import { notificationSelector } from '../selectors'

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
