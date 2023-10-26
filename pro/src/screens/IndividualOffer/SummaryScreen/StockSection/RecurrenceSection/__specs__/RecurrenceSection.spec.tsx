import { render, screen } from '@testing-library/react'
import React from 'react'

import { StockStatsResponseModel } from 'apiClient/v1'

import RecurrenceSection from '../RecurrenceSection'

describe('StockEventSection', () => {
  it('should render all information when there are several stocks', () => {
    const stocksStats: StockStatsResponseModel = {
      stockCount: 2,
      remainingQuantity: undefined,
      oldestStock: '2021-01-01T00:00:00+01:00',
      newestStock: '2021-01-02T00:00:00+01:00',
    }

    render(<RecurrenceSection stocksStats={stocksStats} departementCode="" />)

    expect(screen.queryByText(/Nombre de dates/)).toBeInTheDocument()
    expect(screen.queryByText('2')).toBeInTheDocument()
    expect(screen.queryByText(/Période concernée/)).toBeInTheDocument()
    expect(
      screen.queryByText('du 01/01/2021 au 02/01/2021')
    ).toBeInTheDocument()
    expect(screen.queryByText(/Capacité totale/)).toBeInTheDocument()
    expect(screen.queryByText('Illimitée')).toBeInTheDocument()
  })

  it('should render all information when there are only one stock', () => {
    const stocksStats: StockStatsResponseModel = {
      stockCount: 1,
      remainingQuantity: 637,
      oldestStock: '2021-01-01T00:00:00+01:00',
      newestStock: '2021-01-01T00:00:00+01:00',
    }

    render(<RecurrenceSection stocksStats={stocksStats} departementCode="" />)

    expect(screen.queryByText(/Nombre de dates/)).toBeInTheDocument()
    expect(screen.queryByText('1')).toBeInTheDocument()
    expect(screen.queryByText(/Période concernée/)).toBeInTheDocument()
    expect(screen.queryByText('le 01/01/2021')).toBeInTheDocument()
    expect(screen.queryByText(/Capacité totale/)).toBeInTheDocument()
    expect(screen.queryByText('637 places')).toBeInTheDocument()
  })

  it('should render 1 place', () => {
    const stocksStats: StockStatsResponseModel = {
      stockCount: 27,
      remainingQuantity: 1,
      oldestStock: '2021-01-01T00:00:00+01:00',
      newestStock: '2021-01-01T00:00:00+01:00',
    }

    render(<RecurrenceSection stocksStats={stocksStats} departementCode="" />)

    expect(screen.queryByText('1 place')).toBeInTheDocument()
  })

  it('should not render if there are no stocks', () => {
    render(<RecurrenceSection stocksStats={undefined} departementCode="" />)

    expect(screen.queryByText(/Nombre de dates/)).not.toBeInTheDocument()
  })
})
