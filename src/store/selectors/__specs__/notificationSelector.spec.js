import { notificationV2Selector } from '../notificationSelector'

describe('src | selectors | notification', () => {
  describe('notificationV2Selector', () => {
    it('should return empty state when no notification is stored', () => {
      // given
      const state = { notification: {} }

      // when
      const notification = notificationV2Selector(state)

      // then
      expect(notification).toStrictEqual({})
    })

    it('should return empty state when V1 notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message', version: 1 } }

      // when
      const notification = notificationV2Selector(state)

      // then
      expect(notification).toStrictEqual({})
    })

    it('should return notification details when V2 notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message', version: 2 } }

      // when
      const notification = notificationV2Selector(state)

      // then
      expect(notification).toStrictEqual(state.notification)
    })
  })
})
