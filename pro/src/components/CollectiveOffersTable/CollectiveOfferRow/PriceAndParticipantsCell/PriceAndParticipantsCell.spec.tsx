import { screen } from '@testing-library/react'

import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PriceAndParticipantsCell } from './PriceAndParticipantsCell'

describe('PriceAndParticipantsCell', () => {
  it('should display price and number of participants when present', () => {
    const offer = collectiveOfferFactory({
      stock: {
        numberOfTickets: 5,
        price: 10,
      },
    })

    renderWithProviders(
      <table>
        <tbody>
          <tr>
            <PriceAndParticipantsCell offer={offer} rowId="row-1" />
          </tr>
        </tbody>
      </table>
    )

    expect(screen.getByText('10€')).toBeInTheDocument()
    expect(screen.getByText('5 participants')).toBeInTheDocument()
  })

  it('should display dash when price or numberOfTickets are missing', () => {
    const offer = collectiveOfferFactory({
      stock: {
        price: null,
      },
    })
    renderWithProviders(
      <table>
        <tbody>
          <tr>
            <PriceAndParticipantsCell offer={offer} rowId="row-1" />
          </tr>
        </tbody>
      </table>
    )
    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
