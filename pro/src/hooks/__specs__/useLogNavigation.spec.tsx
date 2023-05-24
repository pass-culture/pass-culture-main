import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'

import * as useAnalytics from 'hooks/useAnalytics'
import useLogNavigation from 'hooks/useLogNavigation'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = jest.fn()

const NavigationLogger = (): null => {
  useLogNavigation()
  return null
}

describe('useLogNavigation', () => {
  it('should log an event on location changes', async () => {
    // When
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))

    renderWithProviders(
      <>
        <NavigationLogger />
        <Routes>
          <Route
            path="*"
            element={
              <>
                <span>Main page</span>
                <Link to="/other_page">Other page</Link>
              </>
            }
          />
          <Route
            path="/other_page"
            element={
              <>
                <span>Other page</span>
                <Link to="/">Accueil</Link>
              </>
            }
          />
        </Routes>
      </>
    )

    const button = screen.getByRole('link', { name: 'Other page' })
    await userEvent.click(button)
    const homeButton = screen.getByRole('link', { name: 'Accueil' })
    await userEvent.click(homeButton)
    expect(mockLogEvent).toHaveBeenCalledTimes(3)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'page_view', {
      from: undefined,
    })
    expect(mockLogEvent).toHaveBeenNthCalledWith(2, 'page_view', {
      from: '/',
    })
    expect(mockLogEvent).toHaveBeenNthCalledWith(3, 'page_view', {
      from: '/other_page',
    })
  })
})
