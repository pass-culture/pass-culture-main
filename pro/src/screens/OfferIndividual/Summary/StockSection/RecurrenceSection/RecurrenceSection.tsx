import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import { FORMAT_DD_MM_YYYY } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

interface IRecurrenceSectionProps {
  offer: IOfferIndividual
}

const sortStocks = (
  a: IOfferIndividualStock,
  b: IOfferIndividualStock
): number => {
  const aDate =
    a.beginningDatetime !== null ? new Date(a.beginningDatetime) : a.dateCreated
  const bDate =
    b.beginningDatetime !== null ? new Date(b.beginningDatetime) : b.dateCreated
  return aDate < bDate ? -1 : 1
}

const RecurrenceSection = ({ offer }: IRecurrenceSectionProps) => {
  if (offer.stocks.length === 0) {
    return null
  }

  const sortedStocks = offer.stocks.sort(sortStocks)

  const totalCapacity = sortedStocks.find(s => s.quantity === null)
    ? 'Illimitée'
    : `${sortedStocks.reduce((a, b) => a + (b.quantity ?? 0), 0)} places`

  let periodText = ''
  if (sortedStocks.length > 1) {
    periodText = `du ${formatLocalTimeDateString(
      sortedStocks[0].beginningDatetime as string,
      offer.venue.departmentCode,
      FORMAT_DD_MM_YYYY
    )} au ${formatLocalTimeDateString(
      sortedStocks[sortedStocks.length - 1].beginningDatetime as string,
      offer.venue.departmentCode,
      FORMAT_DD_MM_YYYY
    )}`
  } else {
    periodText = `le ${formatLocalTimeDateString(
      sortedStocks[0].beginningDatetime as string,
      offer.venue.departmentCode,
      FORMAT_DD_MM_YYYY
    )}`
  }

  return (
    <>
      <SummaryLayout.Row
        title="Nombre de dates"
        description={sortedStocks.length}
      />
      <SummaryLayout.Row title="Période concernée" description={periodText} />
      <SummaryLayout.Row title="Capacité totale" description={totalCapacity} />
    </>
  )
}

export default RecurrenceSection
