import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { UseFrenchQueryTestingExample } from 'components/hooks/__specs/UseFrenchQueryTestingExample'

describe('useFrenchQuery', () => {
  it('should translate french query param to english', () => {
    // When
    render(
      <MemoryRouter
        initialEntries={[
          { pathname: '/accueil', search: '?structure=AY&lieu=BC' },
        ]}
      >
        <UseFrenchQueryTestingExample />
      </MemoryRouter>
    )

    // Then
    expect(screen.getByText('offererId: AY')).toBeInTheDocument()
    expect(screen.getByText('venueId: BC')).toBeInTheDocument()
  })

  it('should allow update on french query params from english', async () => {
    // Given
    render(
      <MemoryRouter
        initialEntries={[
          { pathname: '/accueil', search: '?structure=AY&lieu=BC' },
        ]}
      >
        <UseFrenchQueryTestingExample />
      </MemoryRouter>
    )

    // When
    await userEvent.type(screen.getByLabelText('offererId'), 'DE')
    await userEvent.type(screen.getByLabelText('venueId'), 'FG')
    await userEvent.click(
      screen.getByRole('button', { name: 'Update query params' })
    )

    // Then
    expect(screen.queryByText('offererId: AY')).not.toBeInTheDocument()
    expect(screen.queryByText('venueId: BC')).not.toBeInTheDocument()
    expect(screen.getByText('offererId: DE')).toBeInTheDocument()
    expect(screen.getByText('venueId: FG')).toBeInTheDocument()
  })

  it('should not trigger renders when query did not change', () => {
    // When
    render(
      <MemoryRouter
        initialEntries={[
          { pathname: '/accueil', search: '?structure=AY&lieu=BC' },
        ]}
      >
        <UseFrenchQueryTestingExample />
      </MemoryRouter>
    )

    // Then
    expect(screen.getByText('Number of query changes: 1')).toBeInTheDocument()
  })

  it('should guarantee that setter function identity is stable and won’t change on re-renders to avoid unwanted side effects', () => {
    // When
    render(
      <MemoryRouter
        initialEntries={[
          { pathname: '/accueil', search: '?structure=AY&lieu=BC' },
        ]}
      >
        <UseFrenchQueryTestingExample />
      </MemoryRouter>
    )

    // Then
    expect(
      screen.getByText('Number of setter identities: 1')
    ).toBeInTheDocument()
  })
})
