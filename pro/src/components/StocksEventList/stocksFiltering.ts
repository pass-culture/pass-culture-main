import { PriceCategoryResponseModel } from 'apiClient/v1'

import { StocksEvent } from './StocksEventList'

export enum SortingMode {
  ASC = 'asc',
  DESC = 'desc',
  NONE = 'none',
}

export enum SortingColumn {
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

export const sortStocks = (
  stocks: StocksEvent[],
  priceCategories: PriceCategoryResponseModel[],
  sortingColumn: SortingColumn | null,
  sortingMode: SortingMode
): StocksEvent[] => {
  if (sortingMode === SortingMode.NONE || sortingColumn === null) {
    return sortByBeginningDatetime(stocks, SortingMode.ASC)
  }

  switch (sortingColumn) {
    case SortingColumn.DATE:
      return sortByBeginningDatetime(stocks, sortingMode)
    case SortingColumn.HOUR:
      return sortByHour(stocks, sortingMode)
    case SortingColumn.PRICE_CATEGORY:
      return sortByPriceCategory(stocks, priceCategories, sortingMode)
    case SortingColumn.BOOKING_LIMIT_DATETIME:
      return sortByBookingDatetime(stocks, sortingMode)
    case SortingColumn.QUANTITY:
      return sortByQuantity(stocks, sortingMode)
    default:
      throw new Error('Unknown sorting column')
  }
}
