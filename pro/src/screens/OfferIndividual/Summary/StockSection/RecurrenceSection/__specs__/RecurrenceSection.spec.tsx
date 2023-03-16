import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'

import RecurrenceSection from '../RecurrenceSection'

describe('StockEventSection', () => {
  it('should render all information', () => {
    const offer = individualOfferFactory({
      isEvent: true,
      stocks: [individualStockFactory()],
    })

    render(<RecurrenceSection offer={offer} />)

    expect(screen.queryByText(/Nombre de dates/)).toBeInTheDocument()
    expect(screen.queryByText(/Période concernée/)).toBeInTheDocument()
    expect(screen.queryByText(/Capacité totale/)).toBeInTheDocument()
  })

  it('should not render if there are no stocks', () => {
    const offer = individualOfferFactory({ stocks: [] })

    render(<RecurrenceSection offer={offer} />)

    expect(screen.queryByText(/Nombre de dates/)).not.toBeInTheDocument()
  })
})
