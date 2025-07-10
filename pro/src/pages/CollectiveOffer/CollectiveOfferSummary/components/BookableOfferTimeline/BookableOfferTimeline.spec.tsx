import { render, screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'

import { BookableOfferTimeline } from './BookableOfferTimeline'

describe('BookableOfferTimeline', () => {
  it("should render the 'Suivi de l'offre' title", () => {
    render(<BookableOfferTimeline offer={getCollectiveOfferFactory()} />)
    expect(screen.getByText("Suivi de l'offre")).toBeInTheDocument()
  })

  it.each([
    {
      status: CollectiveOfferDisplayedStatus.PUBLISHED,
      expectedText: 'Publiée',
    },
    {
      status: CollectiveOfferDisplayedStatus.REJECTED,
      expectedText: 'Non conforme',
    },
    {
      status: CollectiveOfferDisplayedStatus.CANCELLED,
      expectedText: 'Annulée',
    },
    {
      status: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      expectedText: 'En instruction',
    },
    {
      status: CollectiveOfferDisplayedStatus.PREBOOKED,
      expectedText: 'Préréservée',
    },
    {
      status: CollectiveOfferDisplayedStatus.BOOKED,
      expectedText: 'Réservée',
    },
    {
      status: CollectiveOfferDisplayedStatus.EXPIRED,
      expectedText: 'Expirée',
    },
    {
      status: CollectiveOfferDisplayedStatus.ENDED,
      expectedText: 'Terminée',
    },
    {
      status: CollectiveOfferDisplayedStatus.ARCHIVED,
      expectedText: 'Archivée',
    },
    {
      status: CollectiveOfferDisplayedStatus.DRAFT,
      expectedText: 'Brouillon',
    },
    {
      status: CollectiveOfferDisplayedStatus.REIMBURSED,
      expectedText: 'Remboursée',
    },
  ])(
    'should render the correct label for past step with status $status',
    ({ status, expectedText }) => {
      render(
        <BookableOfferTimeline
          offer={getCollectiveOfferFactory({
            history: {
              past: [
                {
                  status,
                  datetime: '2025-07-05T13:38:12.020421Z',
                },
              ],
              future: [],
            },
          })}
        />
      )
      expect(screen.getByText(expectedText)).toBeInTheDocument()
    }
  )

  it.each([
    {
      lastStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      expectedWaiting: 'En attente de préréservation',
    },
    {
      lastStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      expectedWaiting: 'En attente de réservation',
    },
    {
      lastStatus: CollectiveOfferDisplayedStatus.ENDED,
      expectedWaiting: 'En attente de remboursement',
    },
  ])(
    'should render a waiting step after $lastStatus if applicable',
    ({ lastStatus, expectedWaiting }) => {
      render(
        <BookableOfferTimeline
          offer={getCollectiveOfferFactory({
            history: {
              past: [
                {
                  status: lastStatus,
                  datetime: '2025-07-05T13:38:12.020421Z',
                },
              ],
              future: [],
            },
          })}
        />
      )
      expect(screen.getByText(expectedWaiting)).toBeInTheDocument()
    }
  )

  it('should not render a waiting step for statuses that do not require it', () => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.CANCELLED,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    expect(screen.queryByText(/En attente de/)).not.toBeInTheDocument()
  })

  it('should render the waiting step "En attente de remboursement" only if 48h have passed after ENDED status', () => {
    const now = new Date()
    const date49hAgo = new Date(now.getTime() - 49 * 60 * 60 * 1000).toISOString()
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.ENDED,
                datetime: date49hAgo,
              },
            ],
            future: [],
          },
        })}
      />
    )
    expect(screen.getByText('En attente de remboursement')).toBeInTheDocument()
  })

  it('should render the waiting step "En attente de préréservation" after PUBLISHED', () => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.PUBLISHED,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    expect(screen.getByText('En attente de préréservation')).toBeInTheDocument()
  })

  it('should render the waiting step "En attente de réservation" after PREBOOKED', () => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.PREBOOKED,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    expect(screen.getByText('En attente de réservation')).toBeInTheDocument()
  })
})

describe('BookableOfferTimeline - step type rendering', () => {
  const getIcon = () => document.querySelector('svg[class*="icon-"]')

  it.each([
    { status: CollectiveOfferDisplayedStatus.CANCELLED, label: 'Annulée' },
    { status: CollectiveOfferDisplayedStatus.EXPIRED, label: 'Expirée' },
    { status: CollectiveOfferDisplayedStatus.REJECTED, label: 'Non conforme' },
  ])('should render an error icon for status $status', ({ status, label }) => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    const icon = getIcon()
    expect(icon).toHaveClass('icon-error')
    expect(screen.getByText(label)).toBeInTheDocument()
  })

  it.each([
    { status: CollectiveOfferDisplayedStatus.BOOKED, label: 'Réservée' },
    { status: CollectiveOfferDisplayedStatus.PUBLISHED, label: 'Publiée' },
    { status: CollectiveOfferDisplayedStatus.PREBOOKED, label: 'Préréservée' },
    { status: CollectiveOfferDisplayedStatus.ENDED, label: 'Terminée' },
    { status: CollectiveOfferDisplayedStatus.REIMBURSED, label: 'Remboursée' },
    { status: CollectiveOfferDisplayedStatus.ARCHIVED, label: 'Archivée' },
  ])('should render a success icon for status $status', ({ status, label }) => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    const icon = getIcon()
    expect(icon).toHaveClass('icon-success')
    expect(screen.getByText(label)).toBeInTheDocument()
  })

  it.each([
    { status: CollectiveOfferDisplayedStatus.DRAFT, label: 'Brouillon' },
    { status: CollectiveOfferDisplayedStatus.UNDER_REVIEW, label: 'En instruction' },
  ])('should render a waiting icon for status $status', ({ status, label }) => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [],
          },
        })}
      />
    )
    const icon = getIcon()
    expect(icon).toHaveClass('icon-waiting')
    expect(screen.getByText(label)).toBeInTheDocument()
  })

  it('should render a disabled icon for future steps', () => {
    render(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.PUBLISHED,
                datetime: '2025-07-05T13:38:12.020421Z',
              },
            ],
            future: [CollectiveOfferDisplayedStatus.PREBOOKED],
          },
        })}
      />
    )
    
    const futureStep = screen.getByText('Préréservée')
    const icon = futureStep.closest('li')?.querySelector('svg')
    expect(icon).toHaveClass('icon-disabled')
  })
})
