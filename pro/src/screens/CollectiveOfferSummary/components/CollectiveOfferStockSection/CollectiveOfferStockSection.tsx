import format from 'date-fns/format'
import React from 'react'

import { GetCollectiveOfferCollectiveStockResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { DEFAULT_RECAP_VALUE } from '../constants'

interface ICollectiveOfferStockSectionProps {
  stock?: GetCollectiveOfferCollectiveStockResponseModel | null
  venueDepartmentCode?: string | null
}

const CollectiveOfferStockSection = ({
  stock,
  venueDepartmentCode,
}: ICollectiveOfferStockSectionProps) => {
  const beginningDateTimeFromUTC = getLocalDepartementDateTimeFromUtc(
    stock?.beginningDatetime,
    venueDepartmentCode
  )
  const bookingLimitDateTimeFromUTC = getLocalDepartementDateTimeFromUtc(
    stock?.bookingLimitDatetime,
    venueDepartmentCode
  )
  return (
    <>
      <SummaryLayout.Row
        title="Date"
        description={
          (beginningDateTimeFromUTC &&
            format(beginningDateTimeFromUTC, FORMAT_DD_MM_YYYY)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryLayout.Row
        title="Horaire"
        description={
          (beginningDateTimeFromUTC &&
            format(beginningDateTimeFromUTC, FORMAT_HH_mm)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryLayout.Row
        title="Nombre de places"
        description={stock?.numberOfTickets || DEFAULT_RECAP_VALUE}
      />
      <SummaryLayout.Row title="Prix total" description={`${stock?.price}€`} />
      <SummaryLayout.Row
        title="Date limite de réservation"
        description={
          (bookingLimitDateTimeFromUTC &&
            format(bookingLimitDateTimeFromUTC, FORMAT_DD_MM_YYYY)) ||
          DEFAULT_RECAP_VALUE
        }
      />
      <SummaryLayout.Row
        title="Détails"
        description={stock?.educationalPriceDetail || DEFAULT_RECAP_VALUE}
      />
    </>
  )
}

export default CollectiveOfferStockSection
