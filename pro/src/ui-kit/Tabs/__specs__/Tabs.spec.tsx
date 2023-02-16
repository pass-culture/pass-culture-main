import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import Tabs from '../Tabs'

describe('src | components | Tabs', () => {
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
})
