import { generatePath } from 'react-router-dom'

import { Offer } from 'core/Offers/types'
import { TStepList, TStepPatternList, Step } from 'new_components/Breadcrumb'

import { OFFER_FORM_STEP_IDS } from './constants'

const isStepAvailable = (
  stepId: string,
  hasOffer: boolean,
  hasStock: boolean
): boolean => {
  if (stepId === OFFER_FORM_STEP_IDS.INFORMATIONS && hasOffer) {
    return true
  }
  if (stepId === OFFER_FORM_STEP_IDS.STOCKS && hasOffer) {
    return true
  }
  if (stepId === OFFER_FORM_STEP_IDS.SUMMARY && hasStock) {
    return true
  }
  return false
}

interface IBuildStepListArgs {
  stepPatternList: TStepPatternList
  offer?: Offer
}
export const buildStepList = ({
  stepPatternList,
  offer,
}: IBuildStepListArgs) => {
  const hasOffer = offer !== undefined
  const hasStock = offer !== undefined && offer.stocks.length > 0

  const stepList = Object.keys(stepPatternList).reduce(
    (acc: TStepList, stepId: string): TStepList => {
      const stepPattern = stepPatternList[stepId]
      const step: Step = {
        id: stepPattern.id,
        label: stepPattern.label,
      }
      if (isStepAvailable(stepId, hasOffer, hasStock) && offer !== undefined) {
        step.url = generatePath(stepPattern.path, { offerId: offer.id })
      }
      return {
        ...acc,
        [stepPattern.id]: step,
      }
    },
    {}
  )

  return stepList
}
