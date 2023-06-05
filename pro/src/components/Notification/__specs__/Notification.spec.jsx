import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import Notification from 'components/Notification/Notification'
import { renderWithProviders } from 'utils/renderWithProviders'

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

describe('src | components | layout | Notification', () => {
  const renderNotification = sentNotification =>
    renderWithProviders(<Notification />, {
      storeOverrides: {
        notification: { notification: sentNotification },
      },
    })

  const notificationTypes = [
    { type: '', role: 'status' },
    { type: 'success', role: 'status' },
    { type: 'error', role: 'alert' },
    { type: 'information', role: 'status' },
    { type: 'pending', role: 'progressbar' },
  ]
  it.each(notificationTypes)(
    'should display given %s text with icon',
    async notificationType => {
      // given
      const sentNotification = {
        text: 'Mon petit succès',
        type: notificationType.type,
        version: 2,
      }

      // when
      renderNotification(sentNotification)

      // then
      const notification = screen.getByText(sentNotification.text)
      expect(notification).toBeInTheDocument()
      expect(notification).toHaveClass('show')
      expect(notification).toHaveClass(
        `is-${notificationType.type || 'success'}`
      )
      expect(notification).toHaveAttribute('role', notificationType.role)
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
