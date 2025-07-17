import { screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { BookableOfferTimeline } from './BookableOfferTimeline'

describe('BookableOfferTimeline', () => {
  it("should render the 'Suivi de l'offre' title", () => {
    renderWithProviders(
      <BookableOfferTimeline offer={getCollectiveOfferFactory()} />
    )
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
      renderWithProviders(
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
      renderWithProviders(
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
    renderWithProviders(
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
    const date49hAgo = new Date(
      now.getTime() - 49 * 60 * 60 * 1000
    ).toISOString()
    renderWithProviders(
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
    renderWithProviders(
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
    renderWithProviders(
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
    renderWithProviders(
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
    renderWithProviders(
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
    {
      status: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      label: 'En instruction',
    },
  ])('should render a waiting icon for status $status', ({ status, label }) => {
    renderWithProviders(
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
    renderWithProviders(
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

  it('should render a infobox if current step is draft', () => {
    renderWithProviders(
      <BookableOfferTimeline
        offer={getCollectiveOfferFactory({
          history: {
            past: [
              {
                status: CollectiveOfferDisplayedStatus.DRAFT,
              },
            ],
            future: [CollectiveOfferDisplayedStatus.PUBLISHED],
          },
        })}
      />
    )

    expect(
      screen.getByText(
        "Vous avez commencé à rédiger un brouillon. Vous pouvez le reprendre à tout moment afin de finaliser sa rédaction et l'envoyer à un établissement."
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Reprendre mon brouillon')).toBeInTheDocument()
  })
})
