import { generatePath, matchPath, useLocation } from 'react-router-dom'

import { OFFER_FORM_STEP_IDS } from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { IStepPattern, Step } from 'new_components/Breadcrumb'

// Build steps for offer creation
// We'll add other builder here for OfferProduct, OfferEvent, etc
const useOfferFormSteps = (
  offer?: IOfferIndividual
): {
  activeSteps: string[]
  currentStep: IStepPattern
  stepList: Step[]
} => {
  const location = useLocation()

  const hasOffer = offer !== undefined
  const hasStock = offer !== undefined && offer.stocks.length > 0

  const stepPatternList: IStepPattern[] = [
    {
      id: OFFER_FORM_STEP_IDS.INFORMATIONS,
      label: 'Informations',
      path: '/offre/:offerId/v3/creation/individuelle/informations',
      isActive: true,
    },
    {
      id: OFFER_FORM_STEP_IDS.STOCKS,
      label: 'Stock & Prix',
      path: '/offre/:offerId/v3/creation/individuelle/stocks',
      isActive: hasOffer,
    },
    {
      id: OFFER_FORM_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
      path: '/offre/:offerId/v3/creation/individuelle/recapitulatif',
      isActive: hasStock,
    },
    {
      id: OFFER_FORM_STEP_IDS.CONFIRMATION,
      label: 'Confirmation',
      isActive: false,
    },
  ]

  let currentStep = stepPatternList.find(
    (stepPattern: IStepPattern) =>
      stepPattern.path && matchPath(location.pathname, stepPattern.path)
  )
  if (!currentStep) currentStep = stepPatternList[0]

  const activeSteps: string[] = stepPatternList
    .filter((stepPattern: IStepPattern): boolean => stepPattern.isActive)
    .map((stepPattern: IStepPattern) => stepPattern.id)

  const stepList = stepPatternList.map((stepPattern: IStepPattern): Step => {
    const step: Step = {
      id: stepPattern.id,
      label: stepPattern.label,
    }
    if (stepPattern.isActive && stepPattern.path && offer) {
      step.url = generatePath(stepPattern.path, { offerId: offer.id })
    }
    return step
  })
  return { activeSteps, currentStep, stepList }
}

export default useOfferFormSteps
