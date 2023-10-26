import React from 'react'

import { StockStatsResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'
import { FORMAT_DD_MM_YYYY } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

interface RecurrenceSectionProps {
  stocksStats?: StockStatsResponseModel
  departementCode: string
}

const RecurrenceSection = ({
  stocksStats,
  departementCode,
}: RecurrenceSectionProps) => {
  if (!stocksStats?.stockCount) {
    return null
  }

  function formatCapacity(capacity: number): string {
    return capacity === 1 ? `${capacity} place` : `${capacity} places`
  }

  const totalCapacity = stocksStats.remainingQuantity
    ? formatCapacity(stocksStats.remainingQuantity)
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
    <>
      <SummaryLayout.Row
        title="Nombre de dates"
        description={stocksStats.stockCount}
      />
      <SummaryLayout.Row title="Période concernée" description={periodText} />
      <SummaryLayout.Row title="Capacité totale" description={totalCapacity} />
    </>
  )
}

export default RecurrenceSection
