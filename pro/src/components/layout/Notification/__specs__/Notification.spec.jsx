import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import Notification from 'components/layout/Notification/Notification'
import { configureTestStore } from 'store/testUtils'

jest.mock('../_constants', () => ({
  NOTIFICATION_SHOW_DURATION: 10,
  NOTIFICATION_TRANSITION_DURATION: 10,
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

  it('should display given text with icon', () => {
    // given
    const sentNotification = {
      text: 'Mon petit succès',
      type: 'success',
      version: 2,
    }

    // when
    renderNotification(sentNotification)

    // then
    const notification = screen.getByText(sentNotification.text)
    expect(notification).toBeInTheDocument()
    expect(notification).toHaveClass('show')
  })

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
