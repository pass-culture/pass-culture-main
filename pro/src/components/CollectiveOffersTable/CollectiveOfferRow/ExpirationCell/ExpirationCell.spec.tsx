import { render, screen } from '@testing-library/react'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'

import { ExpirationCell } from './ExpirationCell'

describe('ExpirationCell', () => {
  const offer: CollectiveOfferResponseModel = collectiveOfferFactory()

  function renderExpirationCell(offerParam = offer, bookingLimitDate: string) {
    return render(
      <table>
        <tbody>
          <tr>
            <ExpirationCell
              offer={offerParam}
              bookingLimitDate={bookingLimitDate}
              rowId="rowId"
            />
          </tr>
        </tbody>
      </table>
    )
  }

  it('should display a banner with the expiration date when it expires in 10 days', () => {
    const offerExpiringIn10Days = { ...offer }
    const in10Days = new Date()
    in10Days.setDate(in10Days.getDate() + 10)

    renderExpirationCell(offerExpiringIn10Days, in10Days.toISOString())

    expect(
      screen.getByText(
        `date limite de réservation : ${in10Days.toLocaleDateString('fr-FR')}`
      )
    ).toBeInTheDocument()
  })

  it('should display a banner with the days left before expiration when it expires in less than 7 days', () => {
    const offerExpiringIn5Days = { ...offer }
    const in5Days = new Date()
    in5Days.setDate(in5Days.getDate() + 5)

    renderExpirationCell(offerExpiringIn5Days, in5Days.toISOString())

    expect(screen.getByText('expire dans 5 jours')).toBeInTheDocument()
  })

  it('should display a banner when it expires today', () => {
    const offerExpiringToday = { ...offer }
    const today = new Date()

    renderExpirationCell(offerExpiringToday, today.toISOString())

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })

  it('should display a banner saying that the offer needs to be booked if it is already pre-booked', () => {
    const offerExpiring = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
    }
    offerExpiring.booking = { booking_status: 'PENDING', id: 1 }
    const today = new Date()

    renderExpirationCell(offerExpiring, today.toISOString())

    expect(
      screen.getByText('En attente de réservation par le chef d’établissement')
    ).toBeInTheDocument()
  })

  it('should not show the expiration days badge if expiration is more than 7 days away', () => {
    const in10Days = new Date()
    in10Days.setDate(in10Days.getDate() + 10)

    renderExpirationCell(offer, in10Days.toISOString())

    expect(screen.queryByText(/expire dans/)).not.toBeInTheDocument()
  })

  it('should show "préréservation par l’enseignant" when offer is PUBLISHED', () => {
    const offerPublished = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    }
    const today = new Date()

    renderExpirationCell(offerPublished, today.toISOString())

    expect(
      screen.getByText('En attente de préréservation par l’enseignant')
    ).toBeInTheDocument()
  })

  it('should apply the "banner-expires-soon" class when expiration is in 2 days', () => {
    const soon = new Date()
    soon.setDate(soon.getDate() + 2)

    const { container } = renderExpirationCell(offer, soon.toISOString())

    expect(container.querySelector('.banner-expires-soon')).toBeInTheDocument()
  })

  it('should display "expire aujourd’hui" if expiration date is in the past (defensive)', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    renderExpirationCell(offer, yesterday.toISOString())

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })
})
