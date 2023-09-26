import cn from 'classnames'
import React from 'react'
import { generatePath, useLocation } from 'react-router-dom'

import Breadcrumb, {
  BreadcrumbStyle,
  StepPattern,
  Step,
} from 'components/Breadcrumb'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveStep from 'hooks/useActiveStep'
import {
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from 'screens/IndividualOffer/InformationsScreen/utils/filterCategories/filterCategories'

import { OFFER_WIZARD_STEP_IDS } from './constants'
import styles from './IndividualOfferBreadcrumb.module.scss'

export const IndividualOfferBreadcrumb = () => {
  const { offer, subcategory } = useIndividualOfferContext()
  const activeStep = useActiveStep(Object.values(OFFER_WIZARD_STEP_IDS))
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

  const steps: StepPattern[] = []

  // First step/tab: informations form or recap
  if (mode === OFFER_WIZARD_MODE.READ_ONLY) {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Détails de l’offre',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      }),
      isActive: true,
    })
  } else {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      label: 'Détails de l’offre',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      }),
      isActive: true,
    })
  }

  // Intermediate steps depending on isEvent
  if (isEvent) {
    steps.push(
      {
        id: OFFER_WIZARD_STEP_IDS.TARIFS,
        label: 'Tarifs',
        path: getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode,
        }),
        isActive: hasOffer,
      },
      {
        id: OFFER_WIZARD_STEP_IDS.STOCKS,
        label: 'Dates & Capacités',
        path: getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode,
        }),
        isActive: hasPriceCategories,
      }
    )
  } else {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.STOCKS,
      label: 'Stock & Prix',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      }),
      isActive: hasOffer,
    })
  }

  // Summary/confirmation steps on creation/draft
  if (mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT) {
    steps.push(
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

  if (mode === OFFER_WIZARD_MODE.READ_ONLY) {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.BOOKINGS,
      label: 'Réservations',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.BOOKINGS,
        mode,
      }),
      isActive: true,
    })
  }

  const stepList = steps.map((stepPattern: StepPattern): Step => {
    const step: Step = {
      id: stepPattern.id,
      label: stepPattern.label,
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
        mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT
          ? BreadcrumbStyle.STEPPER
          : BreadcrumbStyle.TAB
      }
      className={cn(styles['stepper'], {
        [styles['stepper-creation']]:
          mode === OFFER_WIZARD_MODE.CREATION ||
          mode === OFFER_WIZARD_MODE.DRAFT,
        [styles['stepper-readonly']]: mode === OFFER_WIZARD_MODE.READ_ONLY,
      })}
    />
  )
}
