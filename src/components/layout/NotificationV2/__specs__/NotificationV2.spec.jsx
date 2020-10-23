import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'
import { configureTestStore } from 'store/testUtils'

jest.mock('../_constants', () => ({
  NOTIFICATION_SHOW_DURATION: 10,
  NOTIFICATION_TRANSITION_DURATION: 10,
}))

describe('src | components | layout | NotificationV2', () => {
  let props
  let hideNotification
  let store

  beforeEach(() => {
    store = configureTestStore()
    hideNotification = jest.fn()
    props = {
      hideNotification,
      notification: {},
    }
  })

  const renderNotificationV2 = (props, store) => {
    return render(
      <Provider store={store}>
        <NotificationV2Container {...props} />
      </Provider>
    )
  }

  it('should display given text with correct icon', () => {
    // given
    const sentNotification = {
      text: 'Mon petit succès',
      type: 'success',
      version: 2,
    }
    store = configureTestStore({ notification: sentNotification })

    // when
    renderNotificationV2(props, store)

    // then
    const notification = screen.getByText(sentNotification.text)
    expect(notification).toBeInTheDocument()
    expect(notification).toHaveClass('show')
    expect(screen.getByRole('img')).toHaveAttribute(
      'src',
      expect.stringContaining('ico-notification-success-white')
    )
  })

  it('should hide notification after fixed show duration', async () => {
    // given
    const sentNotification = {
      text: 'Mon petit succès',
      type: 'success',
      version: 2,
    }
    store = configureTestStore({ notification: sentNotification })

    // when
    renderNotificationV2(props, store)

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
    store = configureTestStore({ notification: sentNotification })

    // when
    renderNotificationV2(props, store)

    // then
    await waitFor(() => {
      expect(screen.queryByText(sentNotification.text)).not.toBeInTheDocument()
    })
  })
})
