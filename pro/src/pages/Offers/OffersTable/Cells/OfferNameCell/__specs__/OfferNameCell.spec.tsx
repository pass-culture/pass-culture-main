import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { OfferStatus } from 'apiClient/v1'
import {
  collectiveOfferFactory,
  listOffersVenueFactory,
} from 'utils/collectiveApiFactories'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'utils/date'
import {
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { formatLocalTimeDateString } from 'utils/timezone'

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

  it('should show the isbn when the offer has one', () => {
    const eventOffer = listOffersOfferFactory({
      status: OfferStatus.ACTIVE,
      productIsbn: '1234',
      stocks: [listOffersStockFactory({ remainingQuantity: 0 })],
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    expect(screen.getByTestId('offer-isbn')).toBeInTheDocument()
  })

  it('should show the whole date', () => {
    const date = '2024-12-12T13:00:00'
    const eventOffer = listOffersOfferFactory({
      status: OfferStatus.ACTIVE,
      stocks: [
        listOffersStockFactory({
          remainingQuantity: 0,
          beginningDatetime: date,
        }),
      ],
      venue: listOffersVenueFactory({ departementCode: 'FR' }),
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    const expectedDate = formatLocalTimeDateString(
      date,
      'FR',
      FORMAT_DD_MM_YYYY_HH_mm
    )

    expect(screen.getByText(expectedDate)).toBeInTheDocument()
  })

  it('should show the number of dates', () => {
    const eventOffer = listOffersOfferFactory({
      status: OfferStatus.ACTIVE,
      stocks: [
        listOffersStockFactory({
          remainingQuantity: 0,
          beginningDatetime: '2024-12-12T13:00:00',
        }),
        listOffersStockFactory({
          remainingQuantity: 0,
          beginningDatetime: '2024-12-12T13:00:00',
        }),
      ],
      venue: listOffersVenueFactory({ departementCode: 'FR' }),
    })

    renderOfferNameCell({
      offer: eventOffer,
      editionOfferLink: '#',
    })

    expect(screen.queryByText('12/12/2024 14:00')).not.toBeInTheDocument()
    expect(screen.getByText('2 dates')).toBeInTheDocument()
  })
})
