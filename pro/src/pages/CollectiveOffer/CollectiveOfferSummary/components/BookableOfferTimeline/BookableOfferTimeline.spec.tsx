import { render, screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'

import { BookableOfferTimeline } from './BookableOfferTimeline'

describe('BookableOfferTimeline', () => {
  it("should render 'Suivi de l'offre' title", () => {
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
    'should render past step label for status $status',
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
    'should insert a waiting step for $lastStatus',
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

  it('should not insert waiting for other status', () => {
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

  it('should render future steps with disabled style', () => {
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
    expect(screen.getByText('Préréservée')).toBeInTheDocument()
  })
})
