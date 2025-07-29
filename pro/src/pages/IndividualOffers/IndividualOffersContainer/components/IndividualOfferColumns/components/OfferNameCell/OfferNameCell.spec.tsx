import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { OfferStatus } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import { getAddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'
import {
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { formatLocalTimeDateString } from 'commons/utils/timezone'

import { OfferNameCell, OfferNameCellProps } from './OfferNameCell'

const renderOfferNameCell = (
  props: OfferNameCellProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <td>
            <OfferNameCell {...props} />
          </td>
        </tr>
      </tbody>
    </table>,
    {
      initialRouterEntries: ['/offres'],
      ...options,
    }
  )

describe('OfferNameCell', () => {
  it('should display a tag for offer template', () => {
    const eventOffer = listOffersOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
    })

    renderOfferNameCell({
      offer: eventOffer,
      offerLink: '#',
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
      offerLink: '#',
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
      offerLink: '#',
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
      offerLink: '#',
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
      address: getAddressResponseIsLinkedToVenueModelFactory({
        departmentCode: 'FR',
      }),
    })

    renderOfferNameCell({
      offer: eventOffer,
      offerLink: '#',
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
      address: getAddressResponseIsLinkedToVenueModelFactory({
        departmentCode: 'FR',
      }),
    })

    renderOfferNameCell({
      offer: eventOffer,
      offerLink: '#',
    })

    expect(screen.queryByText('12/12/2024 14:00')).not.toBeInTheDocument()
    expect(screen.getByText('2 dates')).toBeInTheDocument()
  })

  it('should use individual offer’s address department code to format a date', () => {
    // Creates an INDIVIDUAL offer
    const individualOffer = listOffersOfferFactory({
      stocks: [
        listOffersStockFactory({
          beginningDatetime: '2024-10-01T10:00:00.000Z', // this datetime is UTC
        }),
      ],
      address: getAddressResponseIsLinkedToVenueModelFactory({
        departmentCode: '972', // Fort-de-France (Martinique) department code (UTC-4 EDT)
      }),
      name: 'Individual offer',
      isEvent: true,
    })

    renderOfferNameCell({
      offer: individualOffer,
      offerLink: '#',
    })

    // We expect here to see 06h00 because for the 01/10/2024, Fort-de-France is UTC-4
    expect(screen.getByText(/01\/10\/2024 06:00/)).toBeInTheDocument()
  })
})
