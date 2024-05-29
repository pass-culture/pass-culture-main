import { screen } from '@testing-library/react'
import React from 'react'

import { defaultGetOffererVenueResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueItem, VenueItemProps } from '../VenueItem'

describe('VenueItem', () => {
  let props: VenueItemProps
  const venueId = 1
  const offererId = 1

  const renderVenueItem = () => renderWithProviders(<VenueItem {...props} />)

  beforeEach(() => {
    props = {
      venue: {
        ...defaultGetOffererVenueResponseModel,
        id: venueId,
        name: 'fake name',
      },
      offererId: offererId,
    }
  })

  it('should render link to see venue details with venue name when no public name provided', () => {
    renderVenueItem()

    const navLink = screen.getAllByRole('link')[0]
    expect(navLink).toHaveTextContent('fake name')
    expect(navLink).toHaveAttribute(
      'href',
      `/structures/${offererId}/lieux/${venueId}`
    )
  })

  it('should render link to see venue details with venue public name when public name provided', () => {
    props.venue.publicName = 'fake public name'

    renderVenueItem()

    const navLink = screen.getAllByRole('link')[0]
    expect(navLink).toHaveTextContent('fake public name')
  })

  it('should redirect to offer creation page', () => {
    renderVenueItem()

    const navLink = screen.getAllByRole('link')[1]
    expect(navLink).toHaveTextContent('Créer une offre')
    expect(navLink).toHaveAttribute(
      'href',
      `/offre/creation?lieu=${venueId}&structure=${offererId}`
    )
  })
})
