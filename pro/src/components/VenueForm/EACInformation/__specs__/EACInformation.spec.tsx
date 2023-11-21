import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { AdageCulturalPartnersResponseModel } from 'apiClient/v1'
import { Venue } from 'core/Venue/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import EACInformation from '../EACInformation'

const renderEACInformation = ({
  venue,
  isCreatingVenue,
}: {
  venue?: Venue | null
  isCreatingVenue: boolean
}) =>
  renderWithProviders(
    <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
  )

describe('components | EACInformation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getEducationalPartners').mockResolvedValue(
      {} as AdageCulturalPartnersResponseModel
    )
  })

  it('should not be able to access information page when creating a venue', () => {
    renderEACInformation({ isCreatingVenue: true, venue: null })

    expect(screen.queryByText(/Renseigner mes informations/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )
  })

  it('should be able to access information page when updating a venue', () => {
    const venue = { id: 'V1' } as unknown as Venue

    renderEACInformation({ isCreatingVenue: false, venue: venue })

    expect(
      screen.queryByText(/Renseigner mes informations/)
    ).not.toHaveAttribute('aria-disabled', 'true')
  })

  it('should have the information banner', () => {
    renderEACInformation({ isCreatingVenue: true, venue: null })

    expect(screen.queryByText(/Une fois votre lieu créé/)).toBeInTheDocument()
  })

  it('should not have the information banner', () => {
    const venue = {
      id: 'V1',
      collectiveAccessInformation: 'test',
      collectiveDescription: 'desc',
      collectiveEmail: 'email@email.email',
    } as unknown as Venue

    renderEACInformation({ isCreatingVenue: false, venue: venue })

    expect(
      screen.queryByText(/Une fois votre lieu créé/)
    ).not.toBeInTheDocument()
  })
})
