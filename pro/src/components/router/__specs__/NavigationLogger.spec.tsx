import '@testing-library/jest-dom'

import { MemoryRouter, Route } from 'react-router'
import { render, screen } from '@testing-library/react'

import { Link } from 'react-router-dom'
import NavigationLogger from '../NavigationLogger'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

const mockLogEvent = jest.fn()

describe('useLogNavigation', () => {
  it('should log an event on location changes', async () => {
    // When
    const store = configureTestStore({ app: { logEvent: mockLogEvent } })
    render(
      <Provider store={store}>
        <MemoryRouter>
          <NavigationLogger />
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

    const button = screen.getByRole('link', { name: 'Structures' })
    await userEvent.click(button)
    const homeButton = screen.getByRole('link', { name: 'Accueil' })
    await userEvent.click(homeButton)
    expect(mockLogEvent).toHaveBeenCalledTimes(3)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'page_view', { from: '/' })
    expect(mockLogEvent).toHaveBeenNthCalledWith(2, 'page_view', {
      from: '/structures',
    })
    expect(mockLogEvent).toHaveBeenNthCalledWith(3, 'page_view', { from: '/' })
  })
})
