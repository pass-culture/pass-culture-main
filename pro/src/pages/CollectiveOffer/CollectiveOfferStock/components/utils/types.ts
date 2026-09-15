import type { CollectiveStockResponseModel } from '@/apiClient/v1'

import type { CollectiveOfferStockFormValues } from '../CollectiveOfferStockForm/validationSchema'

export type CollectiveStockFormDates = Pick<
  CollectiveOfferStockFormValues,
  'bookingLimitDate' | 'endDate' | 'eventTime' | 'startDate'
>

export type CollectiveStockDatetimes = Pick<
  CollectiveStockResponseModel,
  'bookingLimitDatetime' | 'endDatetime' | 'startDatetime'
>
