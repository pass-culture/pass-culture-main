import { screen } from '@testing-library/react'
import React from 'react'

import { IVenue } from 'core/Venue'
import { renderWithProviders } from 'utils/renderWithProviders'

import EACInformation from '../EACInformation'

const renderEACInformation = async ({
  venue,
  isCreatingVenue,
}: {
  venue?: IVenue | null
  isCreatingVenue: boolean
}) =>
  renderWithProviders(
    <EACInformation isCreatingVenue={isCreatingVenue} venue={venue} />
  )

describe('components | EACInformation', () => {
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
    } as unknown as IVenue

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
    } as unknown as IVenue

    await renderEACInformation({
      isCreatingVenue: false,
      venue: venue,
    })

    expect(
      await screen.queryByText(/Une fois votre lieu créé/)
    ).not.toBeInTheDocument()
  })
})
