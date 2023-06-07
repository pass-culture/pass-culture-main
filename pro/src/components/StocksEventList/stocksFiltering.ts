import { PriceCategoryResponseModel } from 'apiClient/v1'
import {
  SortingMode,
  sortColumnByDateString,
  sortColumnByNumber,
} from 'hooks/useColumnSorting'

import { StocksEvent } from './StocksEventList'

export enum StocksEventListSortingColumn {
  DATE = 'DATE',
  HOUR = 'HOUR',
  PRICE_CATEGORY = 'PRICE_CATEGORY',
  BOOKING_LIMIT_DATETIME = 'BOOKING_LIMIT_DATETIME',
  QUANTITY = 'QUANTITY',
}

export const sortStockByPriceCategory = <
  StockWithPriceCategory extends {
    priceCategoryId: string | number
  }
>(
  stocks: StockWithPriceCategory[],
  priceCategories: PriceCategoryResponseModel[],
  sortingMode: SortingMode
): StockWithPriceCategory[] => {
  const priceCategoryIdToPriceMap = priceCategories.reduce(
    (acc, priceCategory) => {
      acc[priceCategory.id] = priceCategory.price
      return acc
    },
    {} as { [key: number]: number }
  )

  return stocks.sort(
    (a, b) =>
      (priceCategoryIdToPriceMap[Number(a.priceCategoryId)] -
        priceCategoryIdToPriceMap[Number(b.priceCategoryId)]) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )
}

export const filterAndSortStocks = (
  stocks: StocksEvent[],
  priceCategories: PriceCategoryResponseModel[],
  sortingColumn: StocksEventListSortingColumn | null,
  sortingMode: SortingMode,
  filters: {
    dateFilter: Date | null
    hourFilter: Date | null
    priceCategoryFilter: string
  }
): StocksEvent[] => {
  const { dateFilter, hourFilter, priceCategoryFilter } = filters
  const filteredStocks = stocks.filter(stock => {
    const stockDate = new Date(stock.beginningDatetime)

    if (dateFilter !== null) {
      const isSameDay =
        stockDate.getFullYear() === dateFilter.getFullYear() &&
        stockDate.getMonth() === dateFilter.getMonth() &&
        stockDate.getDate() === dateFilter.getDate()

      if (!isSameDay) {
        return false
      }
    }

    if (hourFilter !== null) {
      const isSameHour =
        stockDate.getHours() === hourFilter.getHours() &&
        stockDate.getMinutes() === hourFilter.getMinutes()

      if (!isSameHour) {
        return false
      }
    }

    if (
      priceCategoryFilter !== '' &&
      stock.priceCategoryId !== Number(priceCategoryFilter)
    ) {
      return false
    }

    return true
  })

  if (sortingMode === SortingMode.NONE || sortingColumn === null) {
    return sortColumnByDateString(
      filteredStocks,
      'beginningDatetime',
      SortingMode.ASC
    )
  }

  switch (sortingColumn) {
    case StocksEventListSortingColumn.DATE:
    case StocksEventListSortingColumn.HOUR:
      return sortColumnByDateString(
        filteredStocks,
        'beginningDatetime',
        sortingMode
      )
    case StocksEventListSortingColumn.PRICE_CATEGORY:
      return sortStockByPriceCategory(
        filteredStocks,
        priceCategories,
        sortingMode
      )
    case StocksEventListSortingColumn.BOOKING_LIMIT_DATETIME:
      return sortColumnByDateString(
        filteredStocks,
        'bookingLimitDatetime',
        sortingMode
      )
    case StocksEventListSortingColumn.QUANTITY:
      return sortColumnByNumber(filteredStocks, 'quantity', sortingMode)

    default:
      throw new Error('Unknown sorting column')
  }
}
