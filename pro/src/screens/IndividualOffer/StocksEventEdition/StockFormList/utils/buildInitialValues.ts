import { format } from 'date-fns'

import { GetOfferStockResponseModel, OfferStatus } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY, isDateValid } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { StocksEventFormValues } from '../types'

import { setFormReadOnlyFields } from './setFormReadOnlyFields'

interface BuildInitialValuesArgs {
  departementCode?: string | null
  today: Date
  lastProviderName: string | null
  offerStatus: OfferStatus
  priceCategoriesOptions: SelectOption[]
  stocks: GetOfferStockResponseModel[]
}

export const buildInitialValues = ({
  departementCode,
  stocks,
  today,
  lastProviderName,
  offerStatus,
  priceCategoriesOptions,
}: BuildInitialValuesArgs): StocksEventFormValues => ({
  stocks: stocks.map((stock) => {
    const hiddenValues = {
      stockId: stock.id,
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
      priceCategoriesOptions.length === 1
        ? String(priceCategoriesOptions[0]?.value)
        : ''

    return {
      ...hiddenValues,
      remainingQuantity:
        stock.quantity === null || stock.quantity === undefined
          ? ''
          : stock.quantity - stock.bookingsQuantity,
      bookingsQuantity: stock.bookingsQuantity || 0,
      beginningDate: isDateValid(stock.beginningDatetime)
        ? format(
            getLocalDepartementDateTimeFromUtc(
              stock.beginningDatetime,
              departementCode
            ),
            FORMAT_ISO_DATE_ONLY
          )
        : '',
      beginningTime: stock.beginningDatetime
        ? format(
            getLocalDepartementDateTimeFromUtc(
              stock.beginningDatetime,
              departementCode
            ),
            FORMAT_HH_mm
          )
        : '',
      bookingLimitDatetime: stock.bookingLimitDatetime
        ? format(
            getLocalDepartementDateTimeFromUtc(
              stock.bookingLimitDatetime,
              departementCode
            ),
            FORMAT_ISO_DATE_ONLY
          )
        : '',
      priceCategoryId: stock.priceCategoryId
        ? String(stock.priceCategoryId)
        : defaultPriceCategoryOptionId,
    }
  }),
})
