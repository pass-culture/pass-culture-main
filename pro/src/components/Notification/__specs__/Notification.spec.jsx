import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import Notification from 'components/Notification/Notification'
import { configureTestStore } from 'store/testUtils'

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

describe('src | components | layout | Notification', () => {
  let store

  const renderNotification = sentNotification => {
    store = configureTestStore({ notification: sentNotification })

    return render(
      <Provider store={store}>
        <Notification />
      </Provider>
    )
  }

  const notificationTypes = ['', 'success', 'error', 'information', 'pending']
  it.each(notificationTypes)(
    'should display given %s text with icon',
    async type => {
      // given
      const sentNotification = {
        text: 'Mon petit succès',
        type,
        version: 2,
      }

      // when
      renderNotification(sentNotification)

      // then
      const notification = screen.getByText(sentNotification.text)
      expect(notification).toBeInTheDocument()
      expect(notification).toHaveClass('show')
      expect(notification).toHaveClass(`is-${type || 'success'}`)
    }
  )

  it('should hide notification after fixed show duration', async () => {
    // given
    const sentNotification = {
      text: 'Mon petit succès',
      type: 'success',
      version: 2,
    }

    // when
    renderNotification(sentNotification)

    // then
    await waitFor(() => {
      expect(screen.getByText(sentNotification.text)).toHaveClass('hide')
    })
  })

  it('should remove notification after fixed show and transition duration', async () => {
    // given
    const sentNotification = {
      text: 'Mon petit succès',
      type: 'success',
      version: 2,
    }

    // when
    renderNotification(sentNotification)

    // then
    await waitFor(() => {
      expect(screen.queryByText(sentNotification.text)).not.toBeInTheDocument()
    })
  })
})
