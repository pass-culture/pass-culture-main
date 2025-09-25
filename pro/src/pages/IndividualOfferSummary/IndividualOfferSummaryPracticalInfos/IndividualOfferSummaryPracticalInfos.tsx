/* istanbul ignore file */

import type { JSX } from 'react'

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryPracticalInfosScreen } from './components/IndividualOfferSummaryPracticalInfosScreen'

const IndividualOfferSummaryPracticalInfos = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferSummaryPracticalInfosScreen offer={offer} />
      <ActionBar
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryPracticalInfos
