import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { OfferStatus } from 'apiClient/v1'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import {
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferNameCell, OfferNameCellProps } from '../OfferNameCell'

const renderOfferNameCell = (props: OfferNameCellProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferNameCell {...props} />
        </tr>
      </tbody>
    </table>,
    {
      initialRouterEntries: ['/offres'],
    }
  )

describe('OfferNameCell', () => {
  it('should display a tag for offer template', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
    expect(screen.getByText('Offre nom')).toBeInTheDocument()
  })

  it('should display a warning for individual offer with stock sold out', () => {
    const eventOffer = listOffersOfferFactory({
      status: OfferStatus.ACTIVE,
      stocks: [listOffersStockFactory({ remainingQuantity: 0 })],
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    expect(screen.getByRole('img', { name: 'Attention' })).toBeInTheDocument()
  })

  it('should display how many dates have been used up when the warning button is clicked.', async () => {
    const eventOffer = listOffersOfferFactory({
      status: OfferStatus.ACTIVE,
      stocks: [
        listOffersStockFactory({ remainingQuantity: 0 }),
        listOffersStockFactory({ remainingQuantity: 0 }),
      ],
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    await userEvent.click(screen.getByRole('img', { name: 'Attention' }))

    expect(screen.getByText('2 dates épuisées')).toBeInTheDocument()
  })
})
