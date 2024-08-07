import { render, screen } from '@testing-library/react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { ExpirationCell } from '../ExpirationCell'

describe('ExpirationCell', () => {
  const offer: CollectiveOfferResponseModel = collectiveOfferFactory({
    status: CollectiveOfferStatus.ACTIVE,
  })

  function renderExpirationCell(offerParam = offer, bookingLimitDate: string) {
    return render(
      <table>
        <tbody>
          <tr>
            <ExpirationCell
              offer={offerParam}
              bookingLimitDate={bookingLimitDate}
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
      status: CollectiveOfferStatus.SOLD_OUT,
    }
    offerExpiring.booking = { booking_status: 'PENDING', id: 1 }
    const today = new Date()

    renderExpirationCell(offerExpiring, today.toISOString())

    expect(
      screen.getByText('En attente de réservation par le chef d’établissement')
    ).toBeInTheDocument()
  })
})
