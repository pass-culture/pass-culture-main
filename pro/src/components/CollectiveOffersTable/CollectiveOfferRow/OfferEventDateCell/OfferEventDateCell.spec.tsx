import { screen } from '@testing-library/react'

import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferEventDateCell,
  OfferEventDateCellProps,
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
  it('should display 1 date and time when dates are the same', () => {
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
    expect(screen.getByText('15h00')).toBeInTheDocument()
  })

  it('should display both date and time when dates are not the same', () => {
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

    expect(screen.getByText('du 05/08/2024')).toBeInTheDocument()
    expect(screen.getByText('au 06/09/2024')).toBeInTheDocument()
    expect(screen.getByText('01h00')).toBeInTheDocument()
  })

  it('should display "Toute l’année scolaire" if dates are not defined', () => {
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

  it('should not display the time for a template offer starting at midnight UTC', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      name: 'Offre nom',
      dates: {
        start: '2024-08-04T00:00:00Z',
        end: '2024-09-04T00:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('du 04/08/2024')).toBeInTheDocument()
    expect(screen.getByText('au 04/09/2024')).toBeInTheDocument()
    expect(screen.queryByText('00h00')).not.toBeInTheDocument()
  })

  it('should display 1 date and time when dates are the same for a template offer', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      dates: {
        start: '2024-08-04T23:00:00Z',
        end: '2024-08-04T23:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('04/08/2024')).toBeInTheDocument()
    expect(screen.getByText('23h00')).toBeInTheDocument()
  })

  it('should display 1 date and time when dates are the same for a template offer', () => {
    const eventOffer = collectiveOfferFactory({
      isShowcase: true,
      dates: {
        start: '2024-09-04T13:00:00Z',
        end: '2024-09-04T13:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
      rowId: 'rowId',
    })

    expect(screen.getByText('04/09/2024')).toBeInTheDocument()
    expect(screen.getByText('13h00')).toBeInTheDocument()
  })
})
