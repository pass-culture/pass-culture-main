import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { GetOfferStockResponseModel, StocksOrderedBy } from 'apiClient/v1'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { StocksEventList, StocksEventListProps } from '../StocksEventList'

const mockMutate = vi.fn()

vi.mock('apiClient/api', () => ({
  api: {
    getStocks: vi.fn(),
    deleteAllFilteredStocks: vi.fn(),
    deleteStocks: vi.fn(),
    deleteStock: vi.fn(),
  },
}))

vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: () => ({
    mutate: mockMutate,
  }),
}))

// Mock the date to prevent failed tests going from CET to CEST
vi.mock('utils/date', async () => ({
  ...(await vi.importActual('utils/date')),
  getToday: vi.fn(() => new Date('2024-01-01')),
}))

const offerId = 1
const filteredPriceCategoryId = 3
const stock1 = getOfferStockFactory({
  beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
  priceCategoryId: 1,
})
const stock2 = getOfferStockFactory({
  beginningDatetime: new Date('2021-10-14T13:00:00Z').toISOString(),
  priceCategoryId: 2,
})
const stock3 = getOfferStockFactory({
  beginningDatetime: new Date('2021-10-14T12:00:00Z').toISOString(),
  priceCategoryId: filteredPriceCategoryId,
})

const renderStocksEventList = async (
  stocks: GetOfferStockResponseModel[],
  props: Partial<StocksEventListProps> = {}
) => {
  vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
    stocks,
    stockCount: stocks.length,
    hasStocks: true,
  })
  renderWithProviders(
    <StocksEventList
      priceCategories={[
        priceCategoryFactory({ label: 'Label', price: 12.5, id: 1 }),
        priceCategoryFactory({ label: 'Label', price: 5.5, id: 2 }),
        priceCategoryFactory({ label: 'Label', price: 30.5, id: 3 }),
      ]}
      departmentCode={props.departmentCode ?? '78'}
      offer={getIndividualOfferFactory({ id: offerId })}
      {...props}
    />
  )
  await waitFor(() => {
    expect(api.getStocks).toHaveBeenCalledTimes(1)
  })
}

describe('StocksEventList', () => {
  it('should render a table with header and data', async () => {
    await renderStocksEventList([stock1])

    expect(screen.getByText('Date')).toBeInTheDocument()

    expect(await screen.findByText('ven')).toBeInTheDocument()
    expect(screen.getByLabelText('Filtrer par date')).toBeInTheDocument()
    expect(screen.getByLabelText('Filtrer par horaire')).toBeInTheDocument()
    expect(screen.getByText('18')).toBeInTheDocument()
    expect(
      screen.getByText('12,50 € - Label', { selector: 'td' })
    ).toBeInTheDocument()
    expect(screen.getByText('15/09/2021')).toBeInTheDocument()
  })

  it('should render Illimité', async () => {
    await renderStocksEventList([
      getOfferStockFactory({
        priceCategoryId: 1,
        quantity: null,
      }),
    ])

    expect(await screen.findByText('Illimité')).toBeInTheDocument()
  })

  it('should sort stocks', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    await waitFor(() => {
      expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 3 rows
    })
    expect(
      screen.queryAllByRole('img', { name: 'Trier par ordre croissant' })
    ).toHaveLength(
      5 // Number of sortable columns
    )
    within(screen.getAllByRole('row')[1]).getByText('12,50 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('5,50 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,50 € - Label')

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2, stock1, stock3],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.click(
      screen.getAllByRole('img', { name: 'Trier par ordre croissant' })[2]
    )
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        undefined,
        undefined,
        StocksOrderedBy.PRICE_CATEGORY_ID,
        false,
        1
      )
    })
    within(screen.getAllByRole('row')[1]).getByText('5,50 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('12,50 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,50 € - Label')

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock3, stock1, stock2],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre décroissant' })
    )
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        undefined,
        undefined,
        StocksOrderedBy.PRICE_CATEGORY_ID,
        true,
        1
      )
    })
    within(screen.getAllByRole('row')[1]).getByText('30,50 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('12,50 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('5,50 € - Label')

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock1, stock2, stock3],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.click(screen.getByRole('img', { name: 'Ne plus trier' }))
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        undefined,
        undefined,
        StocksOrderedBy.PRICE_CATEGORY_ID,
        false,
        1
      )
    })
    within(screen.getAllByRole('row')[1]).getByText('12,50 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('5,50 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,50 € - Label')
  })

  it('should filter stocks', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    await waitFor(() => {
      expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 3 stock rows
    })

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2, stock3],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.type(
      screen.getByLabelText('Filtrer par date'),
      '2021-10-14'
    )
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        '2021-10-14',
        undefined,
        undefined,
        undefined,
        false,
        1
      )
    })
    expect(screen.getByText('Réinitialiser les filtres')).toBeInTheDocument()
    expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 1 filter result row + 2 stock rows

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.type(screen.getByLabelText('Filtrer par horaire'), '12:00')
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        '2021-10-14',
        '11:00',
        undefined,
        undefined,
        false,
        1
      )
    })
    expect(screen.getAllByRole('row')).toHaveLength(3) // 1 header + 1 filter result row + 1 stock rows

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.selectOptions(
      screen.getByLabelText('Filtrer par tarif'),
      String(filteredPriceCategoryId)
    )
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        '2021-10-14',
        '11:00',
        filteredPriceCategoryId,
        undefined,
        false,
        1
      )
    })
    expect(screen.getAllByRole('row')).toHaveLength(3) // 1 header + 1 filter result row + 1 stock rows
  })

  it('should clear filters', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [],
      stockCount: 0,
      hasStocks: true,
    })
    await userEvent.type(
      screen.getByLabelText('Filtrer par date'),
      '2021-10-14'
    )
    expect(
      await screen.findByText('Réinitialiser les filtres')
    ).toBeInTheDocument()

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock1, stock2, stock3],
      stockCount: 3,
      hasStocks: true,
    })
    await userEvent.click(screen.getByText('Réinitialiser les filtres'))
    expect(
      screen.queryByText('Réinitialiser les filtres')
    ).not.toBeInTheDocument()
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        undefined,
        undefined,
        undefined,
        false,
        1
      )
    })
    expect(screen.getByLabelText('Filtrer par date')).toHaveValue('')
  })

  it('should change checkbox states', async () => {
    await renderStocksEventList([stock1, stock2])
    const selectAllCheckbox = screen.getByLabelText('Tout sélectionner')
    const allCheckboxes = screen.getAllByRole('checkbox')

    // "all checkbox" checks everything
    await userEvent.click(selectAllCheckbox)
    expect(selectAllCheckbox).toBeChecked()
    expect(allCheckboxes[1]).toBeChecked()
    expect(allCheckboxes[2]).toBeChecked()

    // "all checkbox" again unchecks everything
    await userEvent.click(selectAllCheckbox)
    expect(selectAllCheckbox).not.toBeChecked()
    expect(allCheckboxes[1]).not.toBeChecked()
    expect(allCheckboxes[2]).not.toBeChecked()

    // line checkbox partial checks "all checkbox"
    await userEvent.click(allCheckboxes[1])
    expect(selectAllCheckbox).toBeChecked()
    expect(allCheckboxes[1]).toBeChecked()
    expect(allCheckboxes[2]).not.toBeChecked()
  })

  it('should bulk delete lines with filters and use UTC for hour filter when clicking on button on action bar', async () => {
    const stockTime1 = getOfferStockFactory({
      priceCategoryId: 1,
      beginningDatetime: '2021-09-15T10:00:00.000Z',
    })
    const stockTime2 = getOfferStockFactory({
      priceCategoryId: 1,
      beginningDatetime: '2021-10-15T10:00:00.000Z',
    })
    const stockTime3 = getOfferStockFactory({
      priceCategoryId: 1,
      beginningDatetime: '2021-10-15T11:00:00.000Z',
    })
    await renderStocksEventList([stockTime1, stockTime2, stockTime3])
    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stockTime1, stockTime2],
      stockCount: 2,
      hasStocks: true,
    })
    await userEvent.type(screen.getByLabelText('Filtrer par horaire'), '11:00')
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        '10:00',
        undefined,
        undefined,
        false,
        1
      )
    })
    expect(
      screen.getAllByText('12,50 € - Label', { selector: 'td' })
    ).toHaveLength(2)

    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(screen.getByText('2 dates sélectionnées')).toBeInTheDocument()

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [],
      stockCount: 0,
      hasStocks: true,
    })
    await userEvent.click(screen.getByText('Supprimer ces dates'))
    await waitFor(() => {
      expect(api.getStocks).toHaveBeenCalledWith(
        offerId,
        undefined,
        '10:00',
        undefined,
        undefined,
        false,
        1
      )
    })
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(api.deleteStocks).not.toHaveBeenCalled()
    expect(api.deleteAllFilteredStocks).toBeCalledTimes(1)

    // We wanna send it in UTC to the api
    // So if you change department code
    // this doesn't impact the hour filter
    // you should see the same time as in the beginnning datetime (because it's already in utc)
    expect(api.deleteAllFilteredStocks).toHaveBeenCalledWith(1, {
      date: undefined,
      price_category_id: null,
      time: '10:00',
    })

    expect(screen.queryByText('2 dates sélectionnées')).not.toBeInTheDocument()
  })

  it('should bulk delete lines with ids when clicking on each stock', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[1])
    await userEvent.click(checkboxes[3])
    expect(screen.getByText('2 dates sélectionnées')).toBeInTheDocument()

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2],
      stockCount: 1,
      hasStocks: true,
    })
    await userEvent.click(screen.getByText('Supprimer ces dates'))
    expect(api.deleteStock).not.toHaveBeenCalled()
    expect(api.deleteAllFilteredStocks).not.toHaveBeenCalled()
    expect(api.deleteStocks).toBeCalledTimes(1)
    expect(api.deleteStocks).toHaveBeenCalledWith(1, {
      ids_to_delete: [stock1.id, stock3.id],
    })
    expect(api.getStocks).toHaveBeenCalledTimes(1)

    expect(screen.queryByText('2 dates sélectionnées')).not.toBeInTheDocument()
  })

  it('should delete line when clicking on trash icon', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [stock2, stock3],
      stockCount: 2,
      hasStocks: true,
    })
    await userEvent.click(screen.getAllByText('Supprimer')[0])
    expect(api.deleteStock).toHaveBeenCalledWith(stock1.id)
    expect(api.getStocks).toHaveBeenCalledTimes(1)
  })

  it('should reload offer to cancel next step when deleting last offer', async () => {
    await renderStocksEventList([stock1])

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [],
      stockCount: 0,
      hasStocks: false,
    })
    await userEvent.click(screen.getAllByText('Supprimer')[0])
    expect(api.deleteStock).toHaveBeenCalledTimes(1)
    expect(mockMutate).toHaveBeenCalledTimes(1)
  })

  it('should reload offer to cancel next step when bulk deleting last offers', async () => {
    await renderStocksEventList([stock1, stock2, stock3])

    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(screen.getByText('3 dates sélectionnées')).toBeInTheDocument()

    vi.spyOn(api, 'getStocks').mockResolvedValueOnce({
      stocks: [],
      stockCount: 0,
      hasStocks: false,
    })
    await userEvent.click(screen.getByText('Supprimer ces dates'))
    expect(api.deleteAllFilteredStocks).toBeCalledTimes(1)
    expect(mockMutate).toHaveBeenCalledTimes(1)
  })
})
