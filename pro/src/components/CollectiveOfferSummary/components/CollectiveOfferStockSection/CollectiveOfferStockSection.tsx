import format from 'date-fns/format'
import React from 'react'

import { GetCollectiveOfferCollectiveStockResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
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
    <SummaryDescriptionList
      descriptions={[
        {
          title: 'Date',
          text:
            (stock?.beginningDatetime &&
              formatDateTime(stock.beginningDatetime, FORMAT_DD_MM_YYYY)) ||
            DEFAULT_RECAP_VALUE,
        },
        {
          title: 'Horaire',
          text:
            (stock?.beginningDatetime &&
              formatDateTime(stock.beginningDatetime, FORMAT_HH_mm)) ||
            DEFAULT_RECAP_VALUE,
        },
        {
          title: 'Nombre de participants',
          text: stock?.numberOfTickets || DEFAULT_RECAP_VALUE,
        },
        { title: TOTAL_PRICE_LABEL, text: `${stock?.price}€` },
        {
          title: 'Date limite de réservation',
          text:
            (stock?.bookingLimitDatetime &&
              formatDateTime(stock.bookingLimitDatetime, FORMAT_DD_MM_YYYY)) ||
            DEFAULT_RECAP_VALUE,
        },
        {
          title: 'Détails',
          text: stock?.educationalPriceDetail || DEFAULT_RECAP_VALUE,
        },
      ]}
    />
  )
}

export default CollectiveOfferStockSection
