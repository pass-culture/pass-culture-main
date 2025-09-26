import type { JSX } from 'react'

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryScreen } from './components/IndividualOfferSummaryScreen'

const IndividualOfferSummary = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferSummaryScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummary
