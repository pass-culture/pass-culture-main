import { screen } from '@testing-library/react'

import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueOfferSteps } from '../VenueOfferSteps'

const renderVenueOfferSteps = () =>
  renderWithProviders(<VenueOfferSteps />, {
    initialRouterEntries: ['/accueil'],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: {
          ...defaultGetVenue,
          id: 42,
          managingOfferer: { ...defaultGetVenue.managingOfferer, id: 7 },
        },
      },
    },
  })

describe('VenueOfferSteps', () => {
  it('should display both the EAC info link and the DMS timeline link pointing to the venue collective page', () => {
    renderVenueOfferSteps()

    expect(screen.getByText('Prochaines étapes :')).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: 'Renseigner mes informations à destination des enseignants',
      })
    ).toHaveAttribute('href', '/structures/7/lieux/42/collectif')

    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toHaveAttribute('href', '/structures/7/lieux/42/collectif')
  })
})
