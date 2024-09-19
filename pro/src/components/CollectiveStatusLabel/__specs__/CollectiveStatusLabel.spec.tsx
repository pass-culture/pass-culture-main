import { render, screen } from '@testing-library/react'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferStatus,
} from 'apiClient/v1'

import { CollectiveStatusLabel } from '../CollectiveStatusLabel'

interface TestCaseProps {
  status?: CollectiveOfferStatus
  displayedStatus: CollectiveOfferDisplayedStatus
  expectedLabel: string
}

describe('CollectiveStatusLabel', () => {
  const testCases: TestCaseProps[] = [
    {
      displayedStatus: CollectiveOfferDisplayedStatus.PENDING,
      expectedLabel: 'en attente',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.REJECTED,
      expectedLabel: 'refusée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.INACTIVE,
      expectedLabel: 'masquée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.ACTIVE,
      expectedLabel: 'publiée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      expectedLabel: 'préréservée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
      expectedLabel: 'réservée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.EXPIRED,
      expectedLabel: 'expirée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.CANCELLED,
      expectedLabel: 'masquée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.CANCELLED,
      status: CollectiveOfferStatus.ACTIVE,
      expectedLabel: 'publiée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.ARCHIVED,
      expectedLabel: 'archivée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      expectedLabel: 'brouillon',
    },
  ]

  it.each(testCases)(
    'should render %s status',
    ({ displayedStatus, status, expectedLabel }: TestCaseProps) => {
      const unrelevantStatus = CollectiveOfferStatus.PENDING
      render(
        <CollectiveStatusLabel
          offerDisplayedStatus={displayedStatus}
          offerStatus={status ?? unrelevantStatus}
        />
      )
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
})
