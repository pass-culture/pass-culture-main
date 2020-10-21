import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import NotificationV2 from '../NotificationV2'

jest.mock('../_constants', () => ({
  NOTIFICATION_SHOW_DURATION: 10,
  NOTIFICATION_TRANSITION_DURATION: 10,
}))

describe('src | components | layout | NotificationV2', () => {
  let props
  let hideNotification

  beforeEach(() => {
    hideNotification = jest.fn()
    props = {
      hideNotification,
      notification: {},
    }
  })

  describe('success notification', () => {
    it('should display given text with correct icon', () => {
      // given
      props.notification = {
        text: 'Mon petit succès',
        type: 'success',
      }

      // when
      render(<NotificationV2 {...props} />)

      // then
      expect(screen.getByText(props.notification.text)).toBeInTheDocument()
      expect(screen.getByText(props.notification.text).closest('div')).toHaveClass('show')
      expect(screen.getByRole('img')).toHaveAttribute(
        'src',
        expect.stringContaining('ico-notification-success-white')
      )
    })

    it('should hide notification popup after NOTIFICATION_SHOW_DURATION', async () => {
      // given
      props.notification = {
        text: 'Mon petit succès',
        type: 'success',
      }

      // when
      render(<NotificationV2 {...props} />)

      // then
      await waitFor(() => {
        expect(screen.getByText(props.notification.text).closest('div')).toHaveClass('hide')
      })
    })
  })
})
