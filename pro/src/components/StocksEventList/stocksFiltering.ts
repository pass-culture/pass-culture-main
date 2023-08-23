import { PriceCategoryResponseModel } from 'apiClient/v1'
import {
  SortingMode,
  sortColumnByDateString,
  sortColumnByNumber,
} from 'hooks/useColumnSorting'
import { isDateValid } from 'utils/date'

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
  },
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
    dateFilter: string
    hourFilter: string
    priceCategoryFilter: string
  }
): StocksEvent[] => {
  const { dateFilter, hourFilter, priceCategoryFilter } = filters
  const filteredStocks = stocks.filter(stock => {
    const stockDate = new Date(stock.beginningDatetime)
    const [year, month, day] = dateFilter.split('-')
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))

    if (isDateValid(date)) {
      const isSameDay =
        stockDate.getFullYear() === date.getFullYear() &&
        stockDate.getMonth() === date.getMonth() &&
        stockDate.getDate() === date.getDate()

      if (!isSameDay) {
        return false
      }
    }

    const [hours, minutes] = hourFilter.split(':')
    if (hours && minutes) {
      const isSameHour =
        stockDate.getHours() === parseInt(hours) &&
        stockDate.getMinutes() === parseInt(minutes)

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
