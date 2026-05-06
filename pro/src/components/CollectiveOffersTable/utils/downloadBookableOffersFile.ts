import { format } from 'date-fns'

import { apiNew } from '@/apiClient/api'
import type { getCollectiveOffersCsvData } from '@/apiClient/v1/new'
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

  const apiParams: getCollectiveOffersCsvData['query'] = {
    name,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    format: offerFormat,
    locationType,
    offererAddressId,
  }

  const dateTime = format(new Date(), 'yyyyMMdd')

  if (type === 'CSV') {
    const content = (await apiNew.getCollectiveOffersCsv({
      query: apiParams,
    })) as string

    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const fileName = `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.csv`

    downloadFile(blob, fileName)
  } else {
    const content = (await apiNew.getCollectiveOffersExcel({
      query: apiParams,
    })) as Blob

    const fileName = `${BOOKABLE_OFFERS_FILENAME}-${dateTime}.xls`

    downloadFile(content, fileName)
  }
}
