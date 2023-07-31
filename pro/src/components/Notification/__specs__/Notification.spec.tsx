import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import Notification from 'components/Notification/Notification'
import { NotificationTypeEnum } from 'hooks/useNotification'
import { Notification as NotificationType } from 'store/reducers/notificationReducer'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

describe('Notification', () => {
  const renderNotification = (sentNotification: NotificationType) =>
    renderWithProviders(<Notification />, {
      storeOverrides: {
        notification: { notification: sentNotification },
      },
    })

  const notificationTypes = [
    { type: NotificationTypeEnum.SUCCESS, role: 'status' },
    { type: NotificationTypeEnum.ERROR, role: 'alert' },
    { type: NotificationTypeEnum.INFORMATION, role: 'status' },
    { type: NotificationTypeEnum.PENDING, role: 'progressbar' },
  ]
  it.each(notificationTypes)(
    'should display given %s text with icon',
    async notificationType => {
      const sentNotification = {
        text: 'Mon petit succès',
        type: notificationType.type,
        version: 2,
      }

      renderNotification(sentNotification)

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
    const sentNotification = {
      text: 'Mon petit succès',
      type: NotificationTypeEnum.SUCCESS,
      version: 2,
    }

    renderNotification(sentNotification)

    await waitFor(() => {
      expect(screen.getByText(sentNotification.text)).toHaveClass('hide')
    })
  })

  it('should remove notification after fixed show and transition duration', async () => {
    const sentNotification = {
      text: 'Mon petit succès',
      type: NotificationTypeEnum.SUCCESS,
      version: 2,
    }

    renderNotification(sentNotification)

    await waitFor(() => {
      expect(screen.queryByText(sentNotification.text)).not.toBeInTheDocument()
    })
  })
})
