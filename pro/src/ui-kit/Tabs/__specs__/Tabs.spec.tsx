import { screen } from '@testing-library/react'
import React from 'react'

import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as strokeUserIcon } from 'icons/stroke-user.svg'
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
            Icon: strokeUserIcon,
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
