import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { CollectiveOfferStatus } from 'apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'core/Offers/constants'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CollectiveActionsCells,
  CollectiveActionsCellsProps,
} from '../CollectiveActionsCells'

const mockDeselectOffer = vi.fn()
const renderCollectiveActionsCell = (
  props: Partial<CollectiveActionsCellsProps> = {}
) => {
  const defaultProps: CollectiveActionsCellsProps = {
    offer: collectiveOfferFactory(),
    editionOfferLink: '',
    urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    isSelected: false,
    deselectOffer: mockDeselectOffer,
    ...props,
  }

  return renderWithProviders(
    <table>
      <tbody>
        <tr>
          <CollectiveActionsCells {...defaultProps} />
        </tr>
      </tbody>
    </table>
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    patchCollectiveOffersArchive: vi.fn(),
  },
}))

describe('CollectiveActionsCells', () => {
  it('should archive an offer on click on the action', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        stocks: [
          {
            beginningDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    const archiveOfferButton = screen.getByText('Archiver')
    await userEvent.click(archiveOfferButton)

    const modalTitle = screen.getByText(
      'Êtes-vous sûr de vouloir archiver cette offre ?'
    )
    expect(modalTitle).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Archiver l’offre' })
    )

    expect(api.patchCollectiveOffersArchive).toHaveBeenCalledTimes(1)
  })

  it('should deselect an offer selected when the offer has just been archived', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        stocks: [
          {
            beginningDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
      }),
      isSelected: true,
    })

    await userEvent.click(screen.getByTitle('Action'))

    const archiveOfferButton = screen.getByText('Archiver')
    await userEvent.click(archiveOfferButton)

    const modalTitle = screen.getByText(
      'Êtes-vous sûr de vouloir archiver cette offre ?'
    )
    expect(modalTitle).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Archiver l’offre' })
    )

    expect(mockDeselectOffer).toHaveBeenCalledTimes(1)
  })

  it('should not display duplicate button for draft template offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
        status: CollectiveOfferStatus.DRAFT,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(
      screen.queryByText('Créer une offre réservable')
    ).not.toBeInTheDocument()
  })

  it('should not display duplicate button for draft bookable offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        status: CollectiveOfferStatus.DRAFT,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.queryByText('Dupliquer')).not.toBeInTheDocument()
  })

  it('should display duplicate button for template offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.getByText('Créer une offre réservable')).toBeInTheDocument()
  })

  it('should display duplicate button for draft bookable offer', async () => {
    renderCollectiveActionsCell()

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.getByText('Dupliquer')).toBeInTheDocument()
  })
})
