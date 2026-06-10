import { screen } from '@testing-library/react'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AccessibilityCallout } from '../AccessibilityCallout'

const renderAccessibilityCallout = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<AccessibilityCallout />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          ...venueOverrides,
        }),
      },
    },
  })

describe('AccessibilityCallout', () => {
  it('should invite to fill in accessibility when none is defined via acceslibre', () => {
    renderAccessibilityCallout({ externalAccessibilityId: null })

    expect(screen.getByText(/Renseignez/)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Aller sur acceslibre\.beta\.gouv\.fr/ })
    ).toHaveAttribute('href', 'https://acceslibre.beta.gouv.fr/')
  })

  it('should link to the acceslibre edition page when accessibility is defined via acceslibre', () => {
    renderAccessibilityCallout({ externalAccessibilityId: 'slug-123' })

    expect(screen.getByText('Données Acceslibre')).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Éditer sur acceslibre/ })
    ).toHaveAttribute(
      'href',
      'https://acceslibre.beta.gouv.fr/contrib/edit-infos/slug-123/'
    )
  })
})
