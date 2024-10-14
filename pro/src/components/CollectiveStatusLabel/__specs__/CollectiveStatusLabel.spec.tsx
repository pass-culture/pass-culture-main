import { screen } from '@testing-library/react'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

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
    {
      displayedStatus: CollectiveOfferDisplayedStatus.ENDED,
      expectedLabel: 'terminée',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.REIMBURSED,
      expectedLabel: 'terminée',
    },
  ]

  it.each(testCases)(
    'should render %s status',
    ({ displayedStatus, status, expectedLabel }: TestCaseProps) => {
      const unrelevantStatus = CollectiveOfferStatus.PENDING
      renderWithProviders(
        <CollectiveStatusLabel
          offerDisplayedStatus={displayedStatus}
          offerStatus={status ?? unrelevantStatus}
        />
      )
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )

  it('should render "remboursée" status when ff is active', () => {
    const unrelevantStatus = CollectiveOfferStatus.PENDING
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.REIMBURSED}
        offerStatus={unrelevantStatus}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('remboursée')).toBeInTheDocument()
  })

  it('should render "non conforme" status when ff is active for REJECTED displayed status', () => {
    const unrelevantStatus = CollectiveOfferStatus.PENDING
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.REJECTED}
        offerStatus={unrelevantStatus}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('non conforme')).toBeInTheDocument()
  })

  it('should render "en pause" status when ff is active for INACTIVE displayed status', () => {
    const unrelevantStatus = CollectiveOfferStatus.PENDING
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.INACTIVE}
        offerStatus={unrelevantStatus}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('en pause')).toBeInTheDocument()
  })

  it('should render "en instruction" status when ff is active for PENDING displayed status', () => {
    const unrelevantStatus = CollectiveOfferStatus.PENDING
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.PENDING}
        offerStatus={unrelevantStatus}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('en instruction')).toBeInTheDocument()
  })
})
