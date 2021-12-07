import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { NotificationType, Notification } from '../Notification'
import { NotificationComponent } from '../Notification'

jest.mock('../_constants', () => ({
  NOTIFICATION_SHOW_DURATION: 10,
  NOTIFICATION_TRANSITION_DURATION: 10,
}))

describe('src | components | Layout | Notification', () => {
  const renderNotification = (notification: Notification) => {
    render(<NotificationComponent notification={notification} />)
  }

  it('should display given text with icon', () => {
    // given
    const sentNotification = new Notification(
      NotificationType.success,
      'Mon petit succès'
    )

    // when
    renderNotification(sentNotification)

    // then
    const notification = screen.getByText(sentNotification.text)
    expect(notification).toBeInTheDocument()
    expect(notification).toHaveClass('show')
  })

  it('should hide notification after fixed show duration', async () => {
    // given
    const sentNotification = new Notification(
      NotificationType.success,
      'Mon petit succès'
    )

    // when
    renderNotification(sentNotification)

    // then
    await waitFor(() => {
      expect(screen.getByText(sentNotification.text)).toHaveClass('hide')
    })
  })

  it('should remove notification after fixed show and transition duration', async () => {
    // given
    const sentNotification = new Notification(
      NotificationType.success,
      'Mon petit succès'
    )

    // when
    renderNotification(sentNotification)

    // then
    await waitFor(() => {
      expect(screen.queryByText(sentNotification.text)).not.toBeInTheDocument()
    })
  })
})
