import { notificationSelector } from '../notificationSelector'

describe('src | selectors | notification', () => {
  describe('notificationSelector', () => {
    it('should return empty state when no notification is stored', () => {
      // given
      const state = { notification: {} }

      // when
      const notification = notificationSelector(state)

      // then
      expect(notification).toStrictEqual({})
    })

    it('should return notification details when notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message' } }

      // when
      const notification = notificationSelector(state)

      // then
      expect(notification).toStrictEqual(state.notification)
    })
  })
})
