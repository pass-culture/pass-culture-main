import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { CollectiveOfferStatusCell } from '../CollectiveOfferStatusCell'

const renderCollectiveStatusLabel = (offer: CollectiveOfferResponseModel) => {
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
  offerStatus: CollectiveOfferStatus
  bookingStatus?: string
  expectedLabel: string
}

describe('CollectiveStatusLabel', () => {
  const testCases: TestCaseProps[] = [
    { offerStatus: CollectiveOfferStatus.PENDING, expectedLabel: 'en attente' },
    { offerStatus: CollectiveOfferStatus.REJECTED, expectedLabel: 'refusée' },
    {
      offerStatus: CollectiveOfferStatus.INACTIVE,
      expectedLabel: 'désactivée',
    },
    { offerStatus: CollectiveOfferStatus.ACTIVE, expectedLabel: 'publiée' },
    {
      offerStatus: CollectiveOfferStatus.SOLD_OUT,
      expectedLabel: 'préréservée',
      bookingStatus: 'PENDING',
    },
    {
      offerStatus: CollectiveOfferStatus.SOLD_OUT,
      expectedLabel: 'réservée',
      bookingStatus: 'CONFIRMED',
    },
    {
      offerStatus: CollectiveOfferStatus.EXPIRED,
      expectedLabel: 'terminée',
      bookingStatus: 'USED',
    },
    { offerStatus: CollectiveOfferStatus.EXPIRED, expectedLabel: 'expirée' },
    { offerStatus: CollectiveOfferStatus.ARCHIVED, expectedLabel: 'archivée' },
  ]

  it.each(testCases)(
    'should render %s status',
    ({ offerStatus, expectedLabel, bookingStatus }) => {
      const collectiveOffer = collectiveOfferFactory({
        status: offerStatus,
        booking: bookingStatus
          ? { id: 1, booking_status: bookingStatus }
          : null,
      })
      renderCollectiveStatusLabel(collectiveOffer)
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
  it('should throw error is offer status does not exist', () => {
    const collectiveOffer = collectiveOfferFactory({
      status: 'toto' as CollectiveOfferStatus,
    })
    expect(() => renderCollectiveStatusLabel(collectiveOffer)).toThrowError(
      'Le statut de l’offre n’est pas valide'
    )
  })
})
