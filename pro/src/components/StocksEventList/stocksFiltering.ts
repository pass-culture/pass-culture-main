import { PriceCategoryResponseModel } from 'apiClient/v1'
import { SortingMode } from 'hooks/useColumnSorting'

import { StocksEvent } from './StocksEventList'

export enum StocksEventListSortingColumn {
  DATE = 'DATE',
  HOUR = 'HOUR',
  PRICE_CATEGORY = 'PRICE_CATEGORY',
  BOOKING_LIMIT_DATETIME = 'BOOKING_LIMIT_DATETIME',
  QUANTITY = 'QUANTITY',
}

const sortByBeginningDatetime = (
  stocks: StocksEvent[],
  sortingMode: SortingMode
): StocksEvent[] =>
  stocks.sort(
    (a, b) =>
      (Date.parse(a.beginningDatetime) - Date.parse(b.beginningDatetime)) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )

const sortByHour = (
  stocks: StocksEvent[],
  sortingMode: SortingMode
): StocksEvent[] =>
  stocks.sort(
    (a, b) =>
      (Date.parse(a.beginningDatetime) - Date.parse(b.beginningDatetime)) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )

const sortByPriceCategory = (
  stocks: StocksEvent[],
  priceCategories: PriceCategoryResponseModel[],
  sortingMode: SortingMode
): StocksEvent[] => {
  const priceCategoryIdToPriceMap = priceCategories.reduce(
    (acc, priceCategory) => {
      acc[priceCategory.id] = priceCategory.price
      return acc
    },
    {} as { [key: number]: number }
  )

  return stocks.sort(
    (a, b) =>
      (priceCategoryIdToPriceMap[a.priceCategoryId] -
        priceCategoryIdToPriceMap[b.priceCategoryId]) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )
}

const sortByBookingDatetime = (
  stocks: StocksEvent[],
  sortingMode: SortingMode
): StocksEvent[] =>
  stocks.sort(
    (a, b) =>
      (Date.parse(a.beginningDatetime) - Date.parse(b.beginningDatetime)) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )

const sortByQuantity = (
  stocks: StocksEvent[],
  sortingMode: SortingMode
): StocksEvent[] =>
  stocks.sort(
    (a, b) =>
      ((a.quantity ?? Number.MAX_VALUE) - (b.quantity ?? Number.MAX_VALUE)) *
      (sortingMode === SortingMode.ASC ? 1 : -1)
  )

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
    return sortByBeginningDatetime(filteredStocks, SortingMode.ASC)
  }

  switch (sortingColumn) {
    case StocksEventListSortingColumn.DATE:
      return sortByBeginningDatetime(filteredStocks, sortingMode)
    case StocksEventListSortingColumn.HOUR:
      return sortByHour(filteredStocks, sortingMode)
    case StocksEventListSortingColumn.PRICE_CATEGORY:
      return sortByPriceCategory(filteredStocks, priceCategories, sortingMode)
    case StocksEventListSortingColumn.BOOKING_LIMIT_DATETIME:
      return sortByBookingDatetime(filteredStocks, sortingMode)
    case StocksEventListSortingColumn.QUANTITY:
      return sortByQuantity(filteredStocks, sortingMode)
    default:
      throw new Error('Unknown sorting column')
  }
}
