import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import ProfileAndSupport from '../ProfileAndSupport'

const mockLogEvent = jest.fn()

const renderProfileAndSupport = () => {
  const currentUser = {
    id: 'EY',
  }
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser,
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

describe('ProfileAndSupport', () => {
  describe('when the user click on Modifier', () => {
    it('should open a modal with text fields', async () => {
      // When
      jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
        setLogEvent: null,
      }))
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
