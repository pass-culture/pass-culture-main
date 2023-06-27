import { render, screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
import { collectiveOfferFactory } from 'pages/CollectiveOffers/utils/collectiveOffersFactories'

import CollectiveOfferStatusCell from '..'

const renderCollectiveStatusLabel = (offer: Offer) => {
  return render(
    <table>
      <tbody>
        <tr>
          <CollectiveOfferStatusCell offer={offer} />
        </tr>
      </tbody>
    </table>
  )
}

interface TestCaseProps {
  offerStatus: OfferStatus
  bookingStatus?: string
  expectedLabel: string
}

describe('CollectiveStatusLabel', () => {
  const testCases: TestCaseProps[] = [
    { offerStatus: OfferStatus.PENDING, expectedLabel: 'en attente' },
    { offerStatus: OfferStatus.REJECTED, expectedLabel: 'refusée' },
    { offerStatus: OfferStatus.INACTIVE, expectedLabel: 'désactivée' },
    { offerStatus: OfferStatus.ACTIVE, expectedLabel: 'publiée' },
    {
      offerStatus: OfferStatus.SOLD_OUT,
      expectedLabel: 'préréservée',
      bookingStatus: 'PENDING',
    },
    {
      offerStatus: OfferStatus.SOLD_OUT,
      expectedLabel: 'réservée',
      bookingStatus: 'CONFIRMED',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      expectedLabel: 'terminée',
      bookingStatus: 'USED',
    },
    { offerStatus: OfferStatus.EXPIRED, expectedLabel: 'expirée' },
  ]

  it.each(testCases)(
    'should render %s status',
    ({ offerStatus, expectedLabel, bookingStatus }) => {
      const collectiveOffer = collectiveOfferFactory({
        status: offerStatus,
        educationalBooking: bookingStatus
          ? { booking_status: bookingStatus }
          : null,
      })
      renderCollectiveStatusLabel(collectiveOffer)
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
  it('should throw error is offer status does not exist', () => {
    const collectiveOffer = collectiveOfferFactory({
      status: 'toto',
    })
    expect(() => renderCollectiveStatusLabel(collectiveOffer)).toThrowError(
      "Le statut de l'offre n'est pas valide"
    )
  })
})
