import { format } from 'date-fns'

import { api } from '@/apiClient/api'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { downloadFile } from '@/commons/utils/downloadFile'

const BOOKABLE_OFFERS_FILENAME = 'offres-reservables'

export const downloadBookableOffersFile = async (
  filters: CollectiveSearchFiltersParams,
  type: 'CSV' | 'XLS'
): Promise<void> => {
  const {
    name,
    offererId,
    venueId,
    status,
    periodBeginningDate,
    periodEndingDate,
    format: offerFormat,
    locationType,
    offererAddressId,
  } = serializeApiCollectiveFilters(filters)

  const apiParams = [
    name,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    offerFormat,
    locationType,
    offererAddressId,
  ] as const

  const dateTime = format(new Date(), 'yyyyMMdd')

  if (type === 'CSV') {
    const content = await api.getCollectiveOffersCsv(...apiParams)
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const fileName = `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.csv`
    downloadFile(blob, fileName)
  } else {
    const content = await api.getCollectiveOffersExcel(...apiParams)
    const fileName = `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.xls`
    downloadFile(content, fileName)
  }
}
