import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import VenueItem from '../VenueItem'

describe('src | components | pages | OffererCreation | VenueItem', () => {
  let props
  const venueId = 1
  const offererId = 1

  const renderVenueItem = () => renderWithProviders(<VenueItem {...props} />)

  beforeEach(() => {
    props = {
      venue: {
        id: 'AAA',
        nonHumanizedId: venueId,
        managingOffererId: 'ABC',
        name: 'fake name',
        publicName: null,
      },
      offererId: offererId,
    }
  })

  describe('render', () => {
    describe('venue name link', () => {
      it('should render link to see venue details with venue name when no public name provided', () => {
        // given
        renderVenueItem()
        const navLink = screen.getAllByRole('link')[0]

        // then
        expect(navLink).toHaveTextContent('fake name')
        expect(navLink).toHaveAttribute(
          'href',
          `/structures/${offererId}/lieux/${venueId}`
        )
      })

      it('should render link to see venue details with venue public name when public name provided', () => {
        // given
        props.venue.publicName = 'fake public name'

        // when
        renderVenueItem()
        const navLink = screen.getAllByRole('link')[0]

        // then
        expect(navLink).toHaveTextContent('fake public name')
      })
    })

    describe('create new offer in the venue link', () => {
      it('should redirect to offer creation page', () => {
        renderVenueItem()
        const navLink = screen.getAllByRole('link')[1]

        // then
        expect(navLink).toHaveTextContent('Créer une offre')
        expect(navLink).toHaveAttribute(
          'href',
          `/offre/creation?lieu=${venueId}&structure=${offererId}`
        )
      })
    })
  })
})
