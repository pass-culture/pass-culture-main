import { screen } from '@testing-library/react'

import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferEventDateCell,
  type OfferEventDateCellProps,
} from './OfferEventDateCell'

const renderOfferNameCell = (props: OfferEventDateCellProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferEventDateCell {...props} />
        </tr>
      </tbody>
    </table>,
    {
      initialRouterEntries: ['/offres'],
    }
  )

describe('OfferNameCell', () => {
  it('should display 1 date when start and end dates are the same', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: false,
      name: 'Offre nom',
      dates: {
        start: '2024-08-04T13:00:00Z',
        end: '2024-08-04T13:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('04/08/2024')).toBeInTheDocument()
  })

  it('should display 2 dates when start and end dates are not the same', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: false,
      name: 'Offre nom',
      dates: {
        start: '2024-08-04T23:00:00Z',
        end: '2024-09-05T23:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('Du 05/08/2024')).toBeInTheDocument()
    expect(screen.getByText('au 06/09/2024')).toBeInTheDocument()
  })

  it('should display "Toute l’année scolaire" when dates are not defined', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
      dates: null,
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('Toute l’année scolaire')).toBeInTheDocument()
  })
})
