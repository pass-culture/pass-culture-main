import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'
import { Link } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import UtmTracker from '../UtmTracker'

const mockLogEvent = jest.fn()

const renderTracker = (initialEntries: string) => {
  const store = configureTestStore({ app: { logEvent: mockLogEvent } })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[initialEntries]}>
        <UtmTracker />
        <Route path="*">
          <span>Main page</span>
          <Link to="/structures">Structures</Link>
        </Route>
        <Route path="/structures">
          <span>Structure page</span>
          <Link to="/">Accueil</Link>
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('UtmTracker', () => {
  it('should log an event when utm parameters exists', async () => {
    // When
    renderTracker(
      '/structures?utm_campaign=push_offre_local&utm_medium=batch&utm_source=push'
    )
    const homeButton = screen.getByRole('link', { name: 'Accueil' })
    await userEvent.click(homeButton)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.UTM_TRACKING_CAMPAIGN,
      {
        traffic_campaign: 'push_offre_local',
        traffic_medium: 'batch',
        traffic_source: 'push',
      }
    )
  })
  it('should not log an event when utm parameters does not exists', async () => {
    // When
    renderTracker('/structures')
    const homeButton = screen.getByRole('link', { name: 'Accueil' })
    await userEvent.click(homeButton)
    expect(mockLogEvent).toHaveBeenCalledTimes(0)
  })
})
