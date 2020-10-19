import { notificationV1Selector, notificationV2Selector } from '../notificationSelector'

describe('src | selectors | notification', () => {
  describe('notificationV1Selector', () => {
    it('should return null when no notification is stored', () => {
      // given
      const state = { notification: null }

      // when
      const notification = notificationV1Selector(state)

      // then
      expect(notification).toBeNull()
    })

    it('should return null when V2 notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message', version: 2 } }

      // when
      const notification = notificationV1Selector(state)

      // then
      expect(notification).toBeNull()
    })

    it('should return notification details when V1 notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message', version: 1 } }

      // when
      const notification = notificationV1Selector(state)

      // then
      expect(notification).toStrictEqual(state.notification)
    })
  })

  describe('notificationV2Selector', () => {
    it('should return null when no notification is stored', () => {
      // given
      const state = { notification: null }

      // when
      const notification = notificationV2Selector(state)

      // then
      expect(notification).toBeNull()
    })

    it('should return null when V1 notification is stored', () => {
      // given
      const state = { notification: { type: 'success', text: 'My success message', version: 1 } }

      // when
      const notification = notificationV2Selector(state)

      // then
      expect(notification).toBeNull()
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
