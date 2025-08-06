import { screen, waitFor } from '@testing-library/react'

import { NotificationTypeEnum } from '@/commons/hooks/useNotification'
import { Notification as NotificationType } from '@/commons/store/notifications/reducer'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'
import { notificationAdditionalAttributes } from '@/ui-kit/NotificationToaster/NotificationToaster'

describe('Notification', () => {
  const renderNotification = (notification: NotificationType) =>
    renderWithProviders(<Notification />, {
      storeOverrides: {
        notification: { notification, isStickyBarOpen: false },
      },
    })

  const types = Object.keys(
    notificationAdditionalAttributes
  ) as NotificationTypeEnum[]

  it.each(types)('should display given %s text with icon', (type) => {
    const notification = {
      text: 'Mon petit succès',
      type: type,
      duration: 100,
    } satisfies NotificationType

    renderNotification(notification)

    const notificationElement = screen.getByTestId(
      `global-notification-${type}`
    )

    expect(notificationElement).toHaveProperty(
      'role',
      notificationAdditionalAttributes[type].role ?? null
    )

    const notificationContentElement = screen.getByText(notification.text)
    expect(notificationContentElement).toBeInTheDocument()
    expect(notificationContentElement).toHaveClass('show')
    expect(notificationContentElement).toHaveClass(`is-${type}`)
  })

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
