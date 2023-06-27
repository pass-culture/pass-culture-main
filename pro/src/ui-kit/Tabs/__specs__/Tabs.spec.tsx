import { screen } from '@testing-library/react'
import React from 'react'

import LibraryIcon from 'icons/library.svg'
import UserIcon from 'icons/user.svg'
import { renderWithProviders } from 'utils/renderWithProviders'

import Tabs from '../Tabs'

describe('src | components | Tabs', () => {
  it('should render tabs', () => {
    renderWithProviders(
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
    )

    expect(
      screen.getByRole('link', {
        name: 'Offres individuelles',
      })
    ).toHaveAttribute('href', '/offres')
  })
})
