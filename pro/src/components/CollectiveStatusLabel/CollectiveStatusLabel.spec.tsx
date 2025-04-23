import { screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveStatusLabel } from './CollectiveStatusLabel'

interface TestCaseProps {
  displayedStatus: CollectiveOfferDisplayedStatus
  expectedLabel: string
}

describe('CollectiveStatusLabel', () => {
  const testCases: TestCaseProps[] = [
    {
      displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      expectedLabel: 'en instruction',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.REJECTED,
      expectedLabel: 'non conforme',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.HIDDEN,
      expectedLabel: 'en pause',
    },
    {
      displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
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
      expectedLabel: 'remboursée',
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
})
