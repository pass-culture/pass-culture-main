import format from 'date-fns/format'
import React from 'react'

import { GetCollectiveOfferCollectiveStockResponseModel } from 'apiClient/v1'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { TOTAL_PRICE_LABEL } from 'screens/OfferEducationalStock/constants/labels'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { DEFAULT_RECAP_VALUE } from '../constants'

export interface CollectiveOfferStockSectionProps {
  stock?: GetCollectiveOfferCollectiveStockResponseModel | null
  venueDepartmentCode?: string | null
}

const CollectiveOfferStockSection = ({
  stock,
  venueDepartmentCode,
}: CollectiveOfferStockSectionProps) => {
  /* istanbul ignore next: DEBT, TO FIX */
  const formatDateTime = (date: string, dateFormat: string) => {
    return format(
      getLocalDepartementDateTimeFromUtc(
        new Date(date),
        venueDepartmentCode || undefined
      ),
      dateFormat
    )
  }
  /* istanbul ignore next: DEBT, TO FIX */
  return (
    <>
      <SummaryRow
        title="Date"
        description={
          (stock?.beginningDatetime &&
            formatDateTime(stock.beginningDatetime, FORMAT_DD_MM_YYYY)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryRow
        title="Horaire"
        description={
          (stock?.beginningDatetime &&
            formatDateTime(stock.beginningDatetime, FORMAT_HH_mm)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryRow
        title="Nombre de participants"
        description={stock?.numberOfTickets || DEFAULT_RECAP_VALUE}
      />
      <SummaryRow title={TOTAL_PRICE_LABEL} description={`${stock?.price}€`} />
      <SummaryRow
        title="Date limite de réservation"
        description={
          (stock?.bookingLimitDatetime &&
            formatDateTime(stock.bookingLimitDatetime, FORMAT_DD_MM_YYYY)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryRow
        title="Détails"
        description={stock?.educationalPriceDetail || DEFAULT_RECAP_VALUE}
      />
    </>
  )
}

export default CollectiveOfferStockSection
