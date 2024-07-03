import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { CollectiveOfferStatus } from 'apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CollectiveActionsCells,
  CollectiveActionsCellsProps,
} from '../CollectiveActionsCells'

const renderCollectiveActionsCell = ({
  offer,
  editionOfferLink,
  urlSearchFilters,
}: CollectiveActionsCellsProps) => {
  return renderWithProviders(
    <table>
      <tbody>
        <tr>
          <CollectiveActionsCells
            offer={offer}
            editionOfferLink={editionOfferLink}
            urlSearchFilters={urlSearchFilters}
          />
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
      editionOfferLink: '',
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
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

  it('should not show action button', () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
        status: CollectiveOfferStatus.ARCHIVED,
      }),
      editionOfferLink: '',
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
    })

    expect(screen.queryByTitle('Action')).not.toBeInTheDocument()
  })
})
