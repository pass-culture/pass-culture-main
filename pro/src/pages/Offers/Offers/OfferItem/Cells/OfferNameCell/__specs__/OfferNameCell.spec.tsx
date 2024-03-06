import { screen } from '@testing-library/react'
import { add } from 'date-fns'
import React from 'react'

import { CollectiveBookingStatus } from 'apiClient/v1'
import { Audience } from 'core/shared'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferNameCell, OfferNameCellProps } from '../OfferNameCell'

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
  it('should display warning when limit booking date is in less than 7 days', () => {
    const tomorrowFns = add(new Date(), {
      days: 1,
    }).toISOString()

    const eventOffer = collectiveOfferFactory({
      booking: {
        id: 1,
        booking_status: CollectiveBookingStatus.PENDING,
      },
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          beginningDatetime: '2023-12-22T00:00:00Z',
          remainingQuantity: 1,
          bookingLimitDatetime: tomorrowFns,
        },
      ],
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
      audience: Audience.COLLECTIVE,
    })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should not display warning when limit booking date is in more than 7 days', () => {
    const eightDaysFns = add(new Date(), {
      days: 8,
    }).toISOString()

    const eventOffer = collectiveOfferFactory({
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          beginningDatetime: '2022-12-22T00:00:00Z',
          remainingQuantity: 1,
          bookingLimitDatetime: eightDaysFns,
        },
      ],
    })

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
