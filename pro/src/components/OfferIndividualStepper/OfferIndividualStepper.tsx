import React from 'react'
import { generatePath } from 'react-router'

import Breadcrumb, {
  BreadcrumbStyle,
  IStepPattern,
  Step,
} from 'components/Breadcrumb'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'

import { OFFER_WIZARD_STEP_IDS } from './constants'
import { useActiveStep } from './hooks'
import styles from './OfferIndividualStepper.module.scss'

const OfferIndividualStepper = () => {
  const { offer } = useOfferIndividualContext()
  const activeStep = useActiveStep()
  const mode = useOfferWizardMode()
  const hasOffer = offer !== null
  const hasStock = offer !== null && offer.stocks.length > 0

  const stepPatternList: IStepPattern[] = [
    {
      id: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      label: 'Informations',
      path: {
        [OFFER_WIZARD_MODE.CREATION]:
          '/offre/:offerId/v3/creation/individuelle/informations',
        [OFFER_WIZARD_MODE.DRAFT]:
          '/offre/:offerId/v3/brouillon/individuelle/informations',
        [OFFER_WIZARD_MODE.EDITION]:
          '/offre/:offerId/v3/individuelle/informations',
      }[mode],
      isActive: true,
    },
    {
      id: OFFER_WIZARD_STEP_IDS.STOCKS,
      label: 'Stock & Prix',
      path: {
        [OFFER_WIZARD_MODE.CREATION]:
          '/offre/:offerId/v3/creation/individuelle/stocks',
        [OFFER_WIZARD_MODE.DRAFT]:
          '/offre/:offerId/v3/brouillon/individuelle/stocks',
        [OFFER_WIZARD_MODE.EDITION]: '/offre/:offerId/v3/individuelle/stocks',
      }[mode],
      isActive: hasOffer,
    },
  ]

  if (mode !== OFFER_WIZARD_MODE.EDITION) {
    stepPatternList.push(
      {
        id: OFFER_WIZARD_STEP_IDS.SUMMARY,
        label: 'Récapitulatif',
        path: {
          [OFFER_WIZARD_MODE.CREATION]:
            '/offre/:offerId/v3/creation/individuelle/recapitulatif',
          [OFFER_WIZARD_MODE.DRAFT]:
            '/offre/:offerId/v3/brouillon/individuelle/recapitulatif',
        }[mode],
        isActive: hasStock,
      },
      {
        id: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        label: 'Confirmation',
        isActive: false,
      }
    )
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
      styleType={
        mode !== OFFER_WIZARD_MODE.EDITION
          ? BreadcrumbStyle.STEPPER
          : BreadcrumbStyle.DEFAULT
      }
      className={
        mode !== OFFER_WIZARD_MODE.EDITION ? styles['stepper-creation'] : ''
      }
    />
  )
}

export default OfferIndividualStepper
