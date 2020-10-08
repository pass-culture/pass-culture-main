import { render, within } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import Home from '../Home'

describe('src | components | Home', () => {
  it('should render two Cards', async () => {
    // when
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    )

    // then
    const deskLink = within(document.querySelector('a[href="/guichet"]')).queryAllByText(/guichet/i)
    const offersLink = within(document.querySelector('a[href="/offres"]')).queryAllByText(/offres/i)
    expect(deskLink).not.toBeNull()
    expect(offersLink).not.toBeNull()
  })
})
