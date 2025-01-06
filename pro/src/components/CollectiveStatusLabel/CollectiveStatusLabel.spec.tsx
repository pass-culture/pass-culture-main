import { screen } from '@testing-library/react'

import {
  CollectiveOfferDisplayedStatus,
} from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveStatusLabel } from './CollectiveStatusLabel'

interface TestCaseProps {
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
    ({ displayedStatus, expectedLabel }: TestCaseProps) => {
      renderWithProviders(
        <CollectiveStatusLabel offerDisplayedStatus={displayedStatus} />
      )
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )

  it('should render "remboursée" status when ff is active', () => {
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.REIMBURSED}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('remboursée')).toBeInTheDocument()
  })

  it('should render "non conforme" status when ff is active for REJECTED displayed status', () => {
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.REJECTED}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('non conforme')).toBeInTheDocument()
  })

  it('should render "en pause" status when ff is active for INACTIVE displayed status', () => {
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.INACTIVE}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('en pause')).toBeInTheDocument()
  })

  it('should render "en instruction" status when ff is active for PENDING displayed status', () => {
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.PENDING}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('en instruction')).toBeInTheDocument()
  })

  it('should render "annulée" status when the ENABLE_COLLECTIVE_NEW_STATUSES FF is active for a CANCELLED displayed status', () => {
    renderWithProviders(
      <CollectiveStatusLabel
        offerDisplayedStatus={CollectiveOfferDisplayedStatus.CANCELLED}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )
    expect(screen.getByText('annulée')).toBeInTheDocument()
  })
})
