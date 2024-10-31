import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { OfferStatus } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY_HH_mm } from 'commons/utils/date'
import {
  collectiveOfferFactory,
  listOffersVenueFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { AddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'
import {
  getOfferVenueFactory,
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { formatLocalTimeDateString } from 'commons/utils/timezone'

import { OfferNameCell, OfferNameCellProps } from '../OfferNameCell'

const renderOfferNameCell = (
  props: OfferNameCellProps,
  options?: RenderWithProvidersOptions
) =>
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
      ...options,
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

  describe('departmentCode', () => {
    // Creates an COLLECTIVE offer
    const collectiveOffer = collectiveOfferFactory({
      stocks: [
        listOffersStockFactory({
          beginningDatetime: '2024-10-01T10:00:00.000', // this datetime is UTC
        }),
      ],
      name: 'Collective offer',
      venue: listOffersVenueFactory({
        departementCode: '75', // Paris departement code (UTC+2 EDT)
      }),
    })

    // Creates an INDIVIDUAL offer
    const individualOffer = listOffersOfferFactory({
      stocks: [
        listOffersStockFactory({
          beginningDatetime: '2024-10-01T10:00:00.000', // this datetime is UTC
        }),
      ],
      address: AddressResponseIsLinkedToVenueModelFactory({
        departmentCode: '972', // Fort-de-France (Martinique) department code (UTC-4 EDT)
      }),
      name: 'Individual offer',
      isEvent: true,
      venue: {
        offererName: 'Le Piton',
        ...getOfferVenueFactory({
          departementCode: '974', // Saint-Denis (La Réunion) department code (UTC+4 EDT)
        }),
      },
    })

    it('should use collective offer’s venue department code', () => {
      renderOfferNameCell({
        // Using the COLLECTIVE offer that have a venue located at Paris
        offer: collectiveOffer,
        editionOfferLink: '#',
      })

      // We expect here to see 12h00 because for the 01/10/2024, Paris is UTC+2
      expect(
        screen.getByRole('cell', {
          name: /Collective offer 01\/10\/2024 12:00/,
        })
      ).toBeInTheDocument()
    })

    it('should use individual offer’s venue departement code', () => {
      renderOfferNameCell({
        // Using the INDIVIDUAL offer that have VENUE departement code at Saint-Denis (La Réunion)
        offer: individualOffer,
        editionOfferLink: '#',
      })

      // We expect here to see 14h00 because for the 01/10/2024, Saint-Denis is UTC+4
      expect(
        screen.getByRole('cell', {
          name: /Individual offer 01\/10\/2024 14:00/,
        })
      ).toBeInTheDocument()
    })

    it('should use individual offer’s address department code if WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE', () => {
      renderOfferNameCell(
        {
          // Using the same INDIVIDUAL offer that have an address (OA) located at Fort-de-France (Martinique)
          offer: individualOffer,
          editionOfferLink: '#',
        },
        { features: ['WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE'] }
      )

      // We expect here to see 06h00 because for the 01/10/2024, Fort-de-France is UTC-4
      expect(
        screen.getByRole('cell', {
          name: /Individual offer 01\/10\/2024 06:00/,
        })
      ).toBeInTheDocument()
    })
  })
})
