import React from 'react'
import { generatePath } from 'react-router'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import Breadcrumb, {
  BreadcrumbStyle,
  IStepPattern,
  Step,
} from 'new_components/Breadcrumb'

import { OFFER_WIZARD_STEP_IDS } from './constants'
import { useActiveStep } from './hooks'
import useIsCreation from './hooks/useIsCreation'

const OfferIndividualStepper = () => {
  const { offer } = useOfferIndividualContext()
  const activeStep = useActiveStep()
  const isCreation = useIsCreation()
  const hasOffer = offer !== null
  const hasStock = offer !== null && offer.stocks.length > 0

  const stepPatternList: IStepPattern[] = [
    {
      id: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      label: 'Informations',
      path: isCreation
        ? '/offre/:offerId/v3/creation/individuelle/informations'
        : '/offre/:offerId/v3/individuelle/informations',
      isActive: true,
    },
    {
      id: OFFER_WIZARD_STEP_IDS.STOCKS,
      label: 'Stock & Prix',
      path: isCreation
        ? '/offre/:offerId/v3/creation/individuelle/stocks'
        : '/offre/:offerId/v3/individuelle/stocks',
      isActive: hasOffer,
    },
    {
      id: OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
      path: isCreation
        ? '/offre/:offerId/v3/creation/individuelle/recapitulatif'
        : '/offre/:offerId/v3/individuelle/recapitulatif',
      isActive: hasStock,
    },
  ]

  if (isCreation) {
    stepPatternList.push({
      id: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
      label: 'Confirmation',
      isActive: false,
    })
  }

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

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={stepList}
      styleType={BreadcrumbStyle.TAB}
    />
  )
}

export default OfferIndividualStepper
