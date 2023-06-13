import { OfferStatus } from 'apiClient/v1'
import { IOfferIndividualStock } from 'core/Offers/types'
import { SelectOption } from 'custom_types/form'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import { StockEventFormValues } from '../types'
import { setFormReadOnlyFields } from '../utils'

interface BuildInitialValuesCommonArgs {
  departmentCode: string
  today: Date
  lastProviderName: string | null
  offerStatus: OfferStatus
  priceCategoriesOptions: SelectOption[]
}

interface BuildSingleInitialValuesArgs extends BuildInitialValuesCommonArgs {
  stock: IOfferIndividualStock
}

const buildSingleInitialValues = ({
  departmentCode,
  stock,
  today,
  lastProviderName,
  offerStatus,
  priceCategoriesOptions,
}: BuildSingleInitialValuesArgs): StockEventFormValues => {
  const hiddenValues = {
    stockId: stock.nonHumanizedId,
    isDeletable: stock.isEventDeletable,
    readOnlyFields: setFormReadOnlyFields({
      beginningDate: stock.beginningDatetime
        ? new Date(stock.beginningDatetime)
        : null,
      today,
      lastProviderName: lastProviderName,
      offerStatus,
    }),
  }
  const defaultPriceCategoryOptionId =
    priceCategoriesOptions.length === 1 ? priceCategoriesOptions[0].value : ''

  return {
    ...hiddenValues,
    remainingQuantity:
      stock.quantity === null || stock.quantity === undefined
        ? ''
        : stock.quantity - stock.bookingsQuantity,
    bookingsQuantity: stock.bookingsQuantity,
    beginningDate: stock.beginningDatetime
      ? getLocalDepartementDateTimeFromUtc(
          stock.beginningDatetime,
          departmentCode
        )
      : null,
    beginningTime: stock.beginningDatetime
      ? getLocalDepartementDateTimeFromUtc(
          stock.beginningDatetime,
          departmentCode
        )
      : null,
    bookingLimitDatetime: stock.bookingLimitDatetime
      ? getLocalDepartementDateTimeFromUtc(
          stock.bookingLimitDatetime,
          departmentCode
        )
      : null,
    priceCategoryId: stock.priceCategoryId
      ? String(stock.priceCategoryId) ?? defaultPriceCategoryOptionId
      : '',
  }
}

interface BuildInitialValuesArgs extends BuildInitialValuesCommonArgs {
  offerStocks: IOfferIndividualStock[]
}

export const buildInitialValues = ({
  departmentCode,
  offerStocks,
  today,
  lastProviderName,
  offerStatus,
  priceCategoriesOptions,
}: BuildInitialValuesArgs): { stocks: StockEventFormValues[] } => {
  if (offerStocks.length === 0) {
    return {
      stocks: [
        {
          ...STOCK_EVENT_FORM_DEFAULT_VALUES,
          priceCategoryId:
            priceCategoriesOptions.length === 1
              ? String(priceCategoriesOptions[0].value)
              : '',
        },
      ],
    }
  }

  return {
    stocks: offerStocks
      .map(stock =>
        buildSingleInitialValues({
          departmentCode,
          stock,
          today,
          lastProviderName,
          offerStatus,
          priceCategoriesOptions,
        })
      )
      .sort(
        (firstStock, secondStock) =>
          Number(secondStock.beginningDate) - Number(firstStock.beginningDate)
      ),
  }
}
