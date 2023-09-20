import React from 'react'
import { generatePath, useLocation } from 'react-router-dom'

import Breadcrumb, {
  BreadcrumbStyle,
  StepPattern,
  Step,
} from 'components/Breadcrumb'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveStep from 'hooks/useActiveStep'
import useAnalytics from 'hooks/useAnalytics'
import {
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from 'screens/IndividualOffer/Informations/utils/filterCategories/filterCategories'

import { OFFER_WIZARD_STEP_IDS } from './constants'
import styles from './IndividualOfferBreadcrumb.module.scss'

interface IndividualOfferBreadcrumbProps {
  shouldTrack?: boolean
}

const IndividualOfferBreadcrumb = ({
  shouldTrack = true,
}: IndividualOfferBreadcrumbProps) => {
  const { offer, subcategory } = useIndividualOfferContext()
  const activeStep = useActiveStep(Object.values(OFFER_WIZARD_STEP_IDS))
  const { logEvent } = useAnalytics()
  const mode = useOfferWizardMode()
  const hasOffer = offer !== null
  const hasPriceCategories = Boolean(
    offer?.priceCategories && offer?.priceCategories?.length > 0
  )
  const hasStock = offer !== null && offer.stocks.length > 0
  const { search } = useLocation()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')

  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const isEvent =
    offer?.isEvent || subcategory?.isEvent || isOfferSubtypeEvent(offerSubtype)

  const stepPatternList: StepPattern[] = [
    {
      id: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      label: 'Détails de l’offre',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      }),
      isActive: true,
    },
    {
      id: OFFER_WIZARD_STEP_IDS.STOCKS,
      label: isEvent ? 'Dates & Capacités' : 'Stock & Prix',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      }),
      isActive: (isEvent && hasPriceCategories) || (!isEvent && hasOffer),
    },
  ]

  if (isEvent) {
    stepPatternList.splice(1, 0, {
      id: OFFER_WIZARD_STEP_IDS.TARIFS,
      label: 'Tarifs',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      }),
      isActive: hasOffer,
    })
  }

  if (mode !== OFFER_WIZARD_MODE.EDITION) {
    stepPatternList.push(
      {
        id: OFFER_WIZARD_STEP_IDS.SUMMARY,
        label: 'Récapitulatif',
        path: getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode,
        }),
        isActive: hasStock,
      },
      {
        id: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        label: 'Confirmation',
        isActive: false,
      }
    )
  }

  const stepList = stepPatternList.map((stepPattern: StepPattern): Step => {
    const step: Step = {
      id: stepPattern.id,
      label: stepPattern.label,
      onClick: () => {
        shouldTrack &&
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: activeStep,
            to: step.id,
            used: OFFER_FORM_NAVIGATION_MEDIUM.BREADCRUMB,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            offerId: offer?.id,
          })
      },
    }
    if (stepPattern.isActive && stepPattern.path && offer) {
      step.url = generatePath(stepPattern.path, {
        offerId: offer.id,
      })
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
          : BreadcrumbStyle.TAB
      }
      className={
        mode !== OFFER_WIZARD_MODE.EDITION ? styles['stepper-creation'] : ''
      }
    />
  )
}

export default IndividualOfferBreadcrumb
