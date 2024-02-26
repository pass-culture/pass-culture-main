import { screen } from '@testing-library/react'
import { add } from 'date-fns'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { venueFactory } from 'pages/CollectiveOffers/utils/collectiveOffersFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferNameCell, { OfferNameCellProps } from '../OfferNameCell'

const renderOfferNameCell = (props: OfferNameCellProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferNameCell {...props} />
        </tr>
      </tbody>
    </table>,
    {
      initialRouterEntries: ['/offres'],
    }
  )

describe('OfferNameCell', () => {
  let defaultOffer: Offer
  beforeEach(() => {
    defaultOffer = {
      id: 1,
      isActive: true,
      isEditable: true,
      isEvent: true,
      hasBookingLimitDatetimesPassed: false,
      name: 'My little offer',
      thumbUrl: '/my-fake-thumb',
      status: OfferStatus.PENDING,
      educationalBooking: {
        booking_status: OfferStatus.PENDING,
        id: 1,
      },
      stocks: [],
      venue: venueFactory(),
      isEducational: true,
    }
  })

  it('should display warning when limit booking date is in less than 7 days', () => {
    const tomorrowFns = String(
      add(new Date(), {
        days: 1,
      })
    )

    const eventOffer = {
      ...defaultOffer,
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          beginningDatetime: '2023-12-22T00:00:00Z',
          remainingQuantity: 1,
          bookingLimitDatetime: tomorrowFns,
        },
      ],
    }

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
      audience: Audience.COLLECTIVE,
    })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should not display warning when limit booking date is in more than 7 days', () => {
    const eightDaysFns = String(
      add(new Date(), {
        days: 8,
      })
    )

    const eventOffer = {
      ...defaultOffer,
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          beginningDatetime: '2022-12-22T00:00:00Z',
          remainingQuantity: 1,
          bookingLimitDatetime: eightDaysFns,
        },
      ],
    }
    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
      audience: Audience.COLLECTIVE,
    })

    expect(
      screen.queryByRole('img', { name: 'Attention' })
    ).not.toBeInTheDocument()
  })
})
