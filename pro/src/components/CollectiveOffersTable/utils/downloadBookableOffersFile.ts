import { format } from 'date-fns'

import { api } from '@/apiClient/api'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializer'
import { downloadFile } from '@/commons/utils/downloadFile'

const BOOKABLE_OFFERS_FILENAME = 'offres-reservables'

export const downloadBookableOffersFile = async (
  filters: CollectiveSearchFiltersParams,
  defaultFilters: CollectiveSearchFiltersParams,
  type: 'CSV' | 'XLS'
): Promise<void> => {
  const {
    nameOrIsbn,
    offererId,
    venueId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
    collectiveOfferType,
    format: offerFormat,
  } = serializeApiCollectiveFilters(filters, defaultFilters)

  const content =
    type === 'CSV'
      ? await api.getCollectiveOffersCsv(
          nameOrIsbn,
          offererId,
          status,
          venueId,
          creationMode,
          periodBeginningDate,
          periodEndingDate,
          collectiveOfferType,
          offerFormat,
          null, // locationType
          null // offererAddressId
        )
      : await api.getCollectiveOffersExcel(
          nameOrIsbn,
          offererId,
          status,
          venueId,
          creationMode,
          periodBeginningDate,
          periodEndingDate,
          collectiveOfferType,
          offerFormat,
          null, // locationType
          null // offererAddressId
        )

  const dateTime = format(new Date(), 'yyyyMMdd')
  const fileExtension = type === 'CSV' ? 'csv' : 'xls'

  if (type === 'CSV') {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    downloadFile(
      blob,
      `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.${fileExtension}`
    )
  } else {
    downloadFile(
      content,
      `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.${fileExtension}`
    )
  }
}
