import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  individualOfferFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'

import { StocksEventCreation } from '../StocksEventCreation'

describe('StocksEventCreation', () => {
  it('should show help section if there are not stocks', () => {
    render(
      <StocksEventCreation offer={individualOfferFactory({ stocks: [] })} />
    )

    expect(screen.getByText('Comment faire ?')).toBeInTheDocument()
  })

  it('should not show help section if there are stocks already', () => {
    render(
      <StocksEventCreation
        offer={individualOfferFactory({ stocks: [individualStockFactory()] })}
      />
    )

    expect(screen.queryByText('Comment faire ?')).not.toBeInTheDocument()
  })

  it('should open recurrence modal', async () => {
    render(<StocksEventCreation offer={individualOfferFactory()} />)
    expect(
      screen.queryByRole('heading', { name: 'Ajouter une récurrence' })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('Ajouter une récurrence'))
    expect(
      screen.getByRole('heading', { name: 'Ajouter une récurrence' })
    ).toBeInTheDocument()
  })
})
