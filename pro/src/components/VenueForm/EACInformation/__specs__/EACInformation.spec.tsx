import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { AdageCulturalPartnersResponseModel } from 'apiClient/v1'
import { Venue } from 'core/Venue'
import { renderWithProviders } from 'utils/renderWithProviders'

import EACInformation from '../EACInformation'

const renderEACInformation = async ({
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
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({} as AdageCulturalPartnersResponseModel)
  })

  it('should not be able to access information page when creating a venue', async () => {
    await renderEACInformation({
      isCreatingVenue: true,
      venue: null,
    })

    expect(screen.queryByText(/Renseigner mes informations/)).toHaveAttribute(
      'aria-disabled',
      'true'
    )
  })

  it('should be able to access information page when updating a venue', async () => {
    const venue = {
      id: 'V1',
    } as unknown as Venue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(
      screen.queryByText(/Renseigner mes informations/)
    ).not.toHaveAttribute('aria-disabled', 'true')
  })

  it('should have the information banner', async () => {
    await renderEACInformation({
      isCreatingVenue: true,
      venue: null,
    })

    expect(
      await screen.queryByText(/Une fois votre lieu créé/)
    ).toBeInTheDocument()
  })

  it('should not have the information banner', async () => {
    const venue = {
      id: 'V1',
      collectiveAccessInformation: 'test',
      collectiveDescription: 'desc',
      collectiveEmail: 'email@email.email',
    } as unknown as Venue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(
      await screen.queryByText(/Une fois votre lieu créé/)
    ).not.toBeInTheDocument()
  })
})
