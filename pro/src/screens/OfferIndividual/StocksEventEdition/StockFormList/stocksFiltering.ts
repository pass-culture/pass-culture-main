import { PriceCategoryResponseModel } from 'apiClient/v1'
import { sortStockByPriceCategory } from 'components/StocksEventList/stocksFiltering'
import {
  SortingMode,
  sortColumnByDateObject,
  sortColumnByNumber,
} from 'hooks/useColumnSorting'

import { StockEventFormValues } from './types'

export enum StocksEventFormSortingColumn {
  DATE = 'DATE',
  HOUR = 'HOUR',
  PRICE_CATEGORY = 'PRICE_CATEGORY',
  BOOKING_LIMIT_DATETIME = 'BOOKING_LIMIT_DATETIME',
  REMAINING_QUANTITY = 'REMAINING_QUANTITY',
  BOOKINGS_QUANTITY = 'BOOKINGS_QUANTITY',
}

export const filterAndSortStocks = (
  stocks: StockEventFormValues[],
  priceCategories: PriceCategoryResponseModel[],
  sortingColumn: StocksEventFormSortingColumn | null,
  sortingMode: SortingMode,
  filters: {
    dateFilter: Date | null
    hourFilter: Date | null
    priceCategoryFilter: string
  }
): StockEventFormValues[] => {
  const { dateFilter, hourFilter, priceCategoryFilter } = filters
  const filteredStocks = stocks.filter(stock => {
    const stockDate = stock.beginningDate
    if (dateFilter !== null && stockDate instanceof Date) {
      const isSameDay =
        stockDate.getFullYear() === dateFilter.getFullYear() &&
        stockDate.getMonth() === dateFilter.getMonth() &&
        stockDate.getDate() === dateFilter.getDate()

      if (!isSameDay) {
        return false
      }
    }

    const stockHour = stock.beginningTime
    if (hourFilter !== null && stockHour instanceof Date) {
      const isSameHour =
        stockHour.getHours() === hourFilter.getHours() &&
        stockHour.getMinutes() === hourFilter.getMinutes()

      if (!isSameHour) {
        return false
      }
    }

    if (
      priceCategoryFilter !== '' &&
      stock.priceCategoryId !== priceCategoryFilter
    ) {
      return false
    }

    return true
  })

  if (sortingMode === SortingMode.NONE || sortingColumn === null) {
    return sortColumnByDateObject(
      filteredStocks,
      'beginningDate',
      SortingMode.ASC
    )
  }

  switch (sortingColumn) {
    case StocksEventFormSortingColumn.DATE:
      return sortColumnByDateObject(
        filteredStocks,
        'beginningDate',
        sortingMode
      )
    case StocksEventFormSortingColumn.HOUR:
      return sortColumnByDateObject(
        filteredStocks,
        'beginningTime',
        sortingMode
      )
    case StocksEventFormSortingColumn.PRICE_CATEGORY:
      return sortStockByPriceCategory(
        filteredStocks,
        priceCategories,
        sortingMode
      )
    case StocksEventFormSortingColumn.BOOKING_LIMIT_DATETIME:
      return sortColumnByDateObject(
        filteredStocks,
        'bookingLimitDatetime',
        sortingMode
      )
    case StocksEventFormSortingColumn.BOOKINGS_QUANTITY:
      return sortColumnByNumber(filteredStocks, 'bookingsQuantity', sortingMode)
    case StocksEventFormSortingColumn.REMAINING_QUANTITY:
      return sortColumnByNumber(
        filteredStocks,
        'remainingQuantity',
        sortingMode
      )

    default:
      throw new Error('Unknown sorting column')
  }
}
