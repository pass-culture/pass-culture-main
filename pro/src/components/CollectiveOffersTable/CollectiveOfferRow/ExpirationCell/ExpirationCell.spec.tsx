import { screen } from '@testing-library/react'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ExpirationCell } from './ExpirationCell'

describe('ExpirationCell', () => {
  const offer: CollectiveOfferResponseModel = collectiveOfferFactory()

  function renderExpirationCell(offerParam = offer) {
    return renderWithProviders(
      <table>
        <tbody>
          <tr>
            <ExpirationCell offer={offerParam} rowId="rowId" />
          </tr>
        </tbody>
      </table>
    )
  }

  it('should display a banner with the expiration date when it expires in 10 days', () => {
    const in10Days = new Date()
    in10Days.setDate(in10Days.getDate() + 10)

    const offerExpiringIn10Days = {
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: in10Days.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }
    renderExpirationCell(offerExpiringIn10Days)

    expect(
      screen.getByText(
        `date limite de réservation : ${in10Days.toLocaleDateString('fr-FR')}`
      )
    ).toBeInTheDocument()
  })

  it('should display a banner with the days left before expiration when it expires in less than 7 days', () => {
    const in5Days = new Date()
    in5Days.setDate(in5Days.getDate() + 5)

    const offerExpiringIn5Days = {
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: in5Days.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }

    renderExpirationCell(offerExpiringIn5Days)

    expect(screen.getByText('expire dans 5 jours')).toBeInTheDocument()
  })

  it('should display a banner when it expires today', () => {
    const today = new Date()
    const offerExpiringToday = {
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: today.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }

    renderExpirationCell(offerExpiringToday)

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })

  it('should display a banner saying that the offer needs to be booked if it is already pre-booked', () => {
    const today = new Date()

    const offerExpiring = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      stocks: [
        {
          bookingLimitDatetime: today.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }

    renderExpirationCell(offerExpiring)

    expect(
      screen.getByText('En attente de réservation par le chef d’établissement')
    ).toBeInTheDocument()
  })

  it('should not show the expiration days badge if expiration is more than 7 days away', () => {
    const in10Days = new Date()
    in10Days.setDate(in10Days.getDate() + 10)

    renderExpirationCell({
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: in10Days.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    })

    expect(screen.queryByText(/expire dans/)).not.toBeInTheDocument()
  })

  it('should show "préréservation par l’enseignant" when offer is PUBLISHED', () => {
    const today = new Date()

    const offerPublished = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      stocks: [
        {
          bookingLimitDatetime: today.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }

    renderExpirationCell(offerPublished)

    expect(
      screen.getByText('En attente de préréservation par l’enseignant')
    ).toBeInTheDocument()
  })

  it('should apply the "banner-expires-soon" class when expiration is in 2 days', () => {
    const soon = new Date()
    soon.setDate(soon.getDate() + 2)

    const { container } = renderExpirationCell({
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: soon.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    })

    expect(container.querySelector('.banner-expires-soon')).toBeInTheDocument()
  })

  it('should display "expire aujourd’hui" if expiration date is in the past (defensive)', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    renderExpirationCell({
      ...offer,
      stocks: [
        {
          bookingLimitDatetime: yesterday.toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    })

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })
})
