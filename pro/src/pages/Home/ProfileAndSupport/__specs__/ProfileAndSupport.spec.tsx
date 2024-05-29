import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { ProfileAndSupport } from '../ProfileAndSupport'

const mockLogEvent = vi.fn()

const renderProfileAndSupport = () => {
  return renderWithProviders(
    <Routes>
      <Route path="/profil" element={<h1>Page profil</h1>} />
      <Route path="/accueil" element={<ProfileAndSupport />} />
    </Routes>,
    { user: sharedCurrentUserFactory(), initialRouterEntries: ['/accueil'] }
  )
}

describe('ProfileAndSupport', () => {
  it('should redirect to /profil page when the user click on Modifier', async () => {
    // When
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
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
