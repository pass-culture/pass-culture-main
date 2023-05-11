import React from 'react'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'
import { formatLocalTimeDateString } from 'utils/timezone'

interface IStockEventItemProps {
  id?: string
  className?: string
  beginningDatetime: string | Date | null
  price: number
  quantity?: number | null
  bookingLimitDatetime: string | Date | null
  activationCodesExpirationDatetime?: Date | null
  departmentCode: string
  priceCategory?: PriceCategoryResponseModel
}

const StockEventItem = ({
  className,
  beginningDatetime,
  price,
  quantity,
  bookingLimitDatetime,
  departmentCode,
  priceCategory,
}: IStockEventItemProps): JSX.Element => {
  return (
    <div className={className}>
      {beginningDatetime && (
        <SummaryLayout.Row
          title="Date"
          description={formatLocalTimeDateString(
            beginningDatetime,
            departmentCode,
            FORMAT_DD_MM_YYYY
          )}
        />
      )}

      {beginningDatetime && (
        <SummaryLayout.Row
          title="Horaire"
          description={formatLocalTimeDateString(
            beginningDatetime,
            departmentCode,
            FORMAT_HH_mm
          )}
        />
      )}

      {priceCategory ? (
        <SummaryLayout.Row
          title="Tarif"
          description={`${formatPrice(priceCategory.price)} - ${
            priceCategory.label
          }`}
        />
      ) : (
        <SummaryLayout.Row title="Prix" description={formatPrice(price)} />
      )}

      {bookingLimitDatetime !== null && (
        <SummaryLayout.Row
          title="Date limite de réservation"
          description={formatLocalTimeDateString(
            bookingLimitDatetime,
            departmentCode,
            FORMAT_DD_MM_YYYY
          )}
        />
      )}

      <SummaryLayout.Row
        title="Quantité"
        description={quantity ?? 'Illimité'}
      />
    </div>
  )
}

export default StockEventItem
