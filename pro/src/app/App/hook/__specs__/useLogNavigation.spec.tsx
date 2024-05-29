import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Routes, Route, Link } from 'react-router-dom'

import * as useAnalytics from 'app/App/analytics/firebase'
import { useLogNavigation } from 'app/App/hook/useLogNavigation'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = vi.fn()

const NavigationLogger = (): null => {
  useLogNavigation()
  return null
}

const renderLogNavigation = (initialEntries: string = '') => {
  renderWithProviders(
    <>
      <NavigationLogger />
      <Routes>
        <Route
          path="*"
          element={
            <>
              <span>Main page</span>
              <Link to="/other_page/1/toto?text2=bonjour&testId=3">
                Other page
              </Link>
            </>
          }
        />
        <Route
          path="/other_page/:testId/:text"
          element={
            <>
              <span>Other page</span>
              <Link to="/">Accueil</Link>
            </>
          }
        />
      </Routes>
    </>,
    { initialRouterEntries: [initialEntries] }
  )
}

describe('useLogNavigation', () => {
  it('should log an event on page load', () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderLogNavigation()

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      'page_view',
      expect.objectContaining({
        from: undefined,
      })
    )
  })

  it('should log an event containing previous location on location changes', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderLogNavigation()
    const button = screen.getByRole('link', { name: 'Other page' })
    await userEvent.click(button)
    const homeButton = screen.getByRole('link', { name: 'Accueil' })
    await userEvent.click(homeButton)
    expect(mockLogEvent).toHaveBeenCalledTimes(3)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      'page_view',
      expect.objectContaining({
        from: undefined,
      })
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      'page_view',
      expect.objectContaining({
        from: '/',
      })
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      3,
      'page_view',
      expect.objectContaining({
        from: '/other_page/1/toto',
      })
    )
  })

  it('should log an event containing query string and url parameters', () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderWithProviders(
      <NavigationLogger />,
      { initialRouterEntries: ['/other_page/1/toto?text2=bonjour&testId=3'] },
      '/other_page/:testId/:text/'
    )
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      'page_view',
      expect.objectContaining({
        testId: '3',
        text: 'toto',
        text2: 'bonjour',
      })
    )
  })
})
