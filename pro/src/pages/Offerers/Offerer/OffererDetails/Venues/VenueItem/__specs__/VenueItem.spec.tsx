import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { VenueTypeCode } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueItem, { VenueItemProps } from '../VenueItem'

const mockLogEvent = jest.fn()

describe('VenueItem', () => {
  let props: VenueItemProps
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
        collectiveDmsApplications: [],
        hasMissingReimbursementPoint: false,
        hasAdageId: false,
        hasCreatedOffer: false,
        isVirtual: false,
        venueTypeCode: VenueTypeCode.AUTRE,
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

  it('should track when clicking on offer creation page', async () => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))

    renderVenueItem()

    await userEvent.click(screen.getByText('Créer une offre'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Offerer',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'OffererLink',
      }
    )
  })
})
