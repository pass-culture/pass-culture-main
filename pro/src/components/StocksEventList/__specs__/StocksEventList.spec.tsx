import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  individualStockEventListFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'

import StocksEventList, { IStocksEvent } from '../StocksEventList'

interface IrenderStocksEventList {
  stocks: IStocksEvent[]
}

const renderStocksEventList = ({ stocks }: IrenderStocksEventList) =>
  render(
    <StocksEventList
      stocks={stocks}
      priceCategories={[
        priceCategoryFactory({ label: 'Label', price: 12.38, id: 1 }),
      ]}
      departmentCode="78"
    />
  )

describe('StocksEventList', () => {
  it('should render a table with header and data', () => {
    renderStocksEventList({
      stocks: [individualStockEventListFactory({ priceCategoryId: 1 })],
    })

    expect(screen.getByText('Date')).toBeInTheDocument()
    expect(screen.getByText('Horaire')).toBeInTheDocument()
    expect(screen.getByText('Places')).toBeInTheDocument()
    expect(screen.getByText('Tarif')).toBeInTheDocument()
    expect(screen.getByText('Limite de réservation')).toBeInTheDocument()

    expect(screen.getByText('ven')).toBeInTheDocument()
    expect(screen.getByText('15/10/2021')).toBeInTheDocument()
    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('18')).toBeInTheDocument()
    expect(screen.getByText('12,38 € - Label')).toBeInTheDocument()
    expect(screen.getByText('15/09/2021')).toBeInTheDocument()
  })

  it('should render Illimité', () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1, quantity: null }),
      ],
    })

    expect(screen.getByText('Illimité')).toBeInTheDocument()
  })

  it('should manage checkboxes', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    const checkboxes = screen.getAllByRole('checkbox')

    // "all checkbox" check everithing
    await userEvent.click(checkboxes[0])
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // line checkbox uncheck "all checkbox"
    await userEvent.click(checkboxes[1])
    expect(checkboxes[0]).not.toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // line checkbox check "all checkbox"
    await userEvent.click(checkboxes[1])
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // "all checkbox" uncheck everithing
    await userEvent.click(checkboxes[0])
    expect(checkboxes[0]).not.toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
    expect(checkboxes[2]).not.toBeChecked()
  })
})
