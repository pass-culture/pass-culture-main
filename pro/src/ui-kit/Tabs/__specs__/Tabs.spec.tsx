import { screen } from '@testing-library/react'
import React from 'react'

import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
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
            icon: strokeUserIcon,
          },
          {
            label: 'Offres collectives',
            url: '/offres/collectives',
            key: 'collective',
            icon: strokeLibraryIcon,
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
