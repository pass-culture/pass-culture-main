import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PartnerLayout } from './PartnerLayout'

const user = sharedCurrentUserFactory()

const routes: RouteObject[] = [
  {
    path: '/',
    Component: PartnerLayout,
    children: [
      {
        path: 'accueil',
        element: <div data-testid="outlet-content">Page content</div>,
      },
    ],
  },
]

const renderPartnerLayout = () => {
  renderWithProviders(null, {
    routes,
    initialRouterEntries: ['/accueil'],
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    },
  })
}

describe('PartnerLayout', () => {
  it('should render the outlet content', () => {
    renderPartnerLayout()

    expect(screen.getByTestId('outlet-content')).toBeInTheDocument()
  })

  it('should not render any main heading on its own', () => {
    renderPartnerLayout()

    expect(screen.queryByRole('heading', { level: 1 })).not.toBeInTheDocument()
  })
})
