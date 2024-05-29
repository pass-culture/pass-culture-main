import React from 'react'

import { StockStatsResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { FORMAT_DD_MM_YYYY } from 'utils/date'
import { pluralizeString } from 'utils/pluralize'
import { formatLocalTimeDateString } from 'utils/timezone'

interface RecurrenceSectionProps {
  stocksStats?: StockStatsResponseModel
  departementCode: string
}

export const RecurrenceSection = ({
  stocksStats,
  departementCode,
}: RecurrenceSectionProps) => {
  if (!stocksStats?.stockCount && stocksStats?.stockCount !== 0) {
    return null
  }
  const formattedStockCount = new Intl.NumberFormat('fr-FR').format(
    stocksStats.stockCount
  )

  const totalCapacity =
    stocksStats.remainingQuantity || stocksStats.remainingQuantity === 0
      ? new Intl.NumberFormat('fr-FR').format(stocksStats.remainingQuantity) +
        ' ' +
        pluralizeString('place', stocksStats.remainingQuantity)
      : 'Illimitée'

  let periodText = ''
  const { oldestStock, newestStock } = stocksStats
  // when there is only one date the api send oldestStock = newestStock
  if (oldestStock && newestStock && oldestStock !== newestStock) {
    periodText = `du ${formatLocalTimeDateString(
      oldestStock,
      departementCode,
      FORMAT_DD_MM_YYYY
    )} au ${formatLocalTimeDateString(
      newestStock,
      departementCode,
      FORMAT_DD_MM_YYYY
    )}`
  } else if (oldestStock) {
    periodText = `le ${formatLocalTimeDateString(
      oldestStock,
      departementCode,
      FORMAT_DD_MM_YYYY
    )}`
  }

  return (
    <SummaryDescriptionList
      descriptions={[
        { title: 'Nombre de dates', text: formattedStockCount },
        { title: 'Période concernée', text: periodText },
        { title: 'Capacité totale', text: totalCapacity },
      ]}
    />
  )
}
