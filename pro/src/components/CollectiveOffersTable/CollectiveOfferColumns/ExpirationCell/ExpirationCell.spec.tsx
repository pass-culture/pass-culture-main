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
    return renderWithProviders(<ExpirationCell offer={offerParam} />)
  }

  it('should display a banner with the expiration date when it expires in 10 days', () => {
    const in10Days = new Date()
    in10Days.setDate(in10Days.getDate() + 10)

    const offerExpiringIn10Days = {
      ...offer,
      stock: {
        bookingLimitDatetime: in10Days.toISOString(),
      },
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
      stock: {
        bookingLimitDatetime: in5Days.toISOString(),
      },
    }

    renderExpirationCell(offerExpiringIn5Days)

    expect(screen.getByText('expire dans 5 jours')).toBeInTheDocument()
  })

  it('should display a banner when it expires today', () => {
    const today = new Date()
    const offerExpiringToday = {
      ...offer,
      stock: {
        bookingLimitDatetime: today.toISOString(),
      },
    }

    renderExpirationCell(offerExpiringToday)

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })

  it('should display a banner saying that the offer needs to be booked if it is already pre-booked', () => {
    const today = new Date()

    const offerExpiring = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      stock: {
        bookingLimitDatetime: today.toISOString(),
      },
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
      stock: {
        bookingLimitDatetime: in10Days.toISOString(),
      },
    })

    expect(screen.queryByText(/expire dans/)).not.toBeInTheDocument()
  })

  it('should show "préréservation par l’enseignant" when offer is PUBLISHED', () => {
    const today = new Date()

    const offerPublished = {
      ...offer,
      displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      stock: {
        bookingLimitDatetime: today.toISOString(),
      },
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
      stock: {
        bookingLimitDatetime: soon.toISOString(),
      },
    })

    expect(container.querySelector('.banner-expires-soon')).toBeInTheDocument()
  })

  it('should display "expire aujourd’hui" if expiration date is in the past (defensive)', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    renderExpirationCell({
      ...offer,
      stock: {
        bookingLimitDatetime: yesterday.toISOString(),
      },
    })

    expect(screen.getByText('expire aujourd’hui')).toBeInTheDocument()
  })
})
