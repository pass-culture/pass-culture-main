import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import Notification from 'components/Notification/Notification'
import { NotificationTypeEnum } from 'hooks/useNotification'
import { Notification as NotificationType } from 'store/notifications/reducer'
import { renderWithProviders } from 'utils/renderWithProviders'

describe('Notification', () => {
  const renderNotification = (notification: NotificationType) =>
    renderWithProviders(<Notification />, {
      storeOverrides: {
        notification: { notification, isStickyBarOpen: false },
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
    (notificationType) => {
      const notification = {
        text: 'Mon petit succès',
        type: notificationType.type,
        duration: 100,
      } satisfies NotificationType

      renderNotification(notification)

      const notificationElement = screen.getByText(notification.text)
      expect(notificationElement).toBeInTheDocument()
      expect(notificationElement).toHaveClass('show')
      expect(notificationElement).toHaveClass(`is-${notificationType.type}`)
      expect(notificationElement).toHaveAttribute('role', notificationType.role)
    }
  )

  it('should remove notification after fixed show and transition duration', async () => {
    const notification = {
      text: 'Mon petit succès',
      type: NotificationTypeEnum.SUCCESS,
      duration: 100,
    } satisfies NotificationType

    renderNotification(notification)

    await waitFor(() => {
      expect(screen.getByText(notification.text)).toHaveClass('hide')
    })

    await waitFor(() => {
      expect(screen.queryByText(notification.text)).not.toBeInTheDocument()
    })
  })
})
