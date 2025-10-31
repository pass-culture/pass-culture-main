import { screen } from '@testing-library/react'

import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferDateCell, type OfferEventDateCellProps } from './OfferDateCell'

const renderOfferNameCell = (props: OfferEventDateCellProps) =>
  renderWithProviders(<OfferDateCell {...props} />, {
    initialRouterEntries: ['/offres'],
  })

describe('OfferEventDateCell', () => {
  it('should display 1 date when start and end dates are the same', () => {
    const eventOffer = collectiveOfferFactory({
      name: 'Offre nom',
      dates: {
        start: '2024-08-04T13:00:00Z',
        end: '2024-08-04T13:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
    })

    expect(screen.getByText('04/08/2024')).toBeInTheDocument()
  })

  it('should display 2 dates when start and end dates are not the same', () => {
    const eventOffer = collectiveOfferFactory({
      name: 'Offre nom',
      dates: {
        start: '2024-08-04T23:00:00Z',
        end: '2024-09-05T23:00:00Z',
      },
    })

    renderOfferNameCell({
      offer: eventOffer,
    })

    expect(screen.getByText('Du 05/08/2024')).toBeInTheDocument()
    expect(screen.getByText('au 06/09/2024')).toBeInTheDocument()
  })

  it('should display "Toute l’année scolaire" for OfferTemplate when dates are not defined', () => {
    const offer = collectiveOfferTemplateFactory({
      name: 'Offre nom',
      dates: null,
    })

    renderOfferNameCell({
      offer,
    })

    expect(screen.getByText('Toute l’année scolaire')).toBeInTheDocument()
  })

  it('should display "-" for Offer when dates are not defined', () => {
    const eventOffer = collectiveOfferFactory({
      name: 'Offre nom',
      dates: null,
    })

    renderOfferNameCell({
      offer: eventOffer,
    })

    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
