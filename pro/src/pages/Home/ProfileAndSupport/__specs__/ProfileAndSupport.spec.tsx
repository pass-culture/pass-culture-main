import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import ProfileAndSupport from '../ProfileAndSupport'

const mockLogEvent = vi.fn()

const renderProfileAndSupport = () => {
  const currentUser = {
    id: 'EY',
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
  }

  return renderWithProviders(
    <Routes>
      <Route path="/profil" element={<h1>Page profil</h1>} />
      <Route path="/accueil" element={<ProfileAndSupport />} />
    </Routes>,
    { storeOverrides, initialRouterEntries: ['/accueil'] }
  )
}

describe('ProfileAndSupport', () => {
  it('should redirect to /profil page when the user click on Modifier', async () => {
    // When
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    renderProfileAndSupport()
    const editButton = screen.getByRole('link', { name: 'Modifier' })
    expect(editButton).toHaveAttribute('href', '/profil')
    await userEvent.click(editButton)

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EDIT_PROFILE)
    expect(screen.getByText('Page profil')).toBeInTheDocument()
  })
})
