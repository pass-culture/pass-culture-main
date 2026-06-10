import { screen } from '@testing-library/react'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AccessibilitySubSection } from './AccessibilitySubSection'

const renderAccessibilitySubSection = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<AccessibilitySubSection />, {
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

describe('AccessibilitySubSection', () => {
  it('should display the internal accessibility section when there is no acceslibre data', () => {
    renderAccessibilitySubSection({ externalAccessibilityData: null })

    expect(screen.getByText('Non accessible')).toBeInTheDocument()
  })

  it('should display the acceslibre callout for a permanent venue', () => {
    renderAccessibilitySubSection({
      externalAccessibilityData: null,
      isPermanent: true,
    })

    expect(screen.getByText(/Renseignez/)).toBeInTheDocument()
  })

  it('should not display the acceslibre callout for a non-permanent venue', () => {
    renderAccessibilitySubSection({
      externalAccessibilityData: null,
      isPermanent: false,
    })

    expect(screen.queryByText(/Renseignez/)).not.toBeInTheDocument()
  })

  it('should display the external accessibility section when acceslibre data is present', () => {
    renderAccessibilitySubSection({
      externalAccessibilityId: 'slug-123',
      externalAccessibilityData: { isAccessibleMotorDisability: true },
    })

    expect(screen.getByText(/Modalités/)).toBeInTheDocument()
    expect(screen.getByText('Handicap moteur')).toBeInTheDocument()
  })
})
