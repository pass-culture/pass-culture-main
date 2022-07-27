import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import Tabs from '../Tabs'

describe('src | new_components | Tabs', () => {
  it('should render tabs', () => {
    render(
      <MemoryRouter>
        <Tabs
          tabs={[
            {
              label: 'Offres individuelles',
              url: '/offres',
              key: 'individual',
              Icon: UserIcon,
            },
            {
              label: 'Offres collectives',
              url: '/offres/collectives',
              key: 'collective',
              Icon: LibraryIcon,
            },
          ]}
        />
      </MemoryRouter>
    )
    expect(
      screen.getByRole('link', {
        name: 'Offres individuelles',
      })
    ).toHaveAttribute('href', '/offres')
  })
  it('should use query params', () => {
    render(
      <MemoryRouter
        initialEntries={['http://localhost:3001/offres?filter=test']}
      >
        <Tabs
          tabs={[
            {
              label: 'Offres individuelles',
              url: '/offres',
              key: 'individual',
              Icon: UserIcon,
            },
            {
              label: 'Offres collectives',
              url: '/offres/collectives',
              key: 'collective',
              Icon: LibraryIcon,
            },
          ]}
          withQueryParams
        />
      </MemoryRouter>
    )
    expect(
      screen.getByRole('link', {
        name: 'Offres collectives',
      })
    ).toHaveAttribute('href', '/offres/collectives?filter=test')
  })
})
