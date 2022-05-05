import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import ProfileAndSupport from '../ProfileAndSupport'

const mockLogEvent = jest.fn()

const renderProfileAndSupport = () => {
  const currentUser = {
    id: 'EY',
  }
  const store = configureTestStore({
    data: {
      users: [currentUser],
    },
    user: {
      initialized: true,
    },
    app: {
      logEvent: mockLogEvent,
    },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <ProfileAndSupport />
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | pages | Home | ProfileAndSupport', () => {
  describe('when the user click on Modifier', () => {
    it('should open a modal with text fields', async () => {
      // When
      renderProfileAndSupport()
      const editButton = screen.getByRole('button', { name: 'Modifier' })
      userEvent.click(editButton)
      await waitFor(() => expect(mockLogEvent).toHaveBeenCalledTimes(1))
      // Then
      expect(screen.getAllByRole('textbox')).toHaveLength(4)
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EDIT_PROFILE)
    })
  })
})
