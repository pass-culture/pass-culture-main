import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import NotFound from '../NotFound'

describe('src | components | pages | NotFound', () => {
  it('should display a message notifying the user they are on a wrong path and add a link to home', () => {
    // when
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    )
    // then
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Oh non !'
    )
    expect(screen.getByRole('link')).toHaveAttribute('href', '/accueil')
    expect(screen.getByText('Cette page n’existe pas.')).toBeInTheDocument()
  })

  it('should display a link with the redirect props url if not default', () => {
    // when
    const props = {
      redirect: '/mon/autre/url',
    }
    render(
      <MemoryRouter>
        <NotFound {...props} />
      </MemoryRouter>
    )

    // then
    expect(screen.getByRole('link')).toHaveAttribute('href', '/mon/autre/url')
  })
})
