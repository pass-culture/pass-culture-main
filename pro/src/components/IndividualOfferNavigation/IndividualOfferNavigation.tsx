import React from 'react'
import { generatePath, useLocation } from 'react-router-dom'

import { Step, StepPattern, Stepper } from 'components/Stepper/Stepper'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useActiveStep } from 'hooks/useActiveStep'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import {
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from 'screens/IndividualOffer/InformationsScreen/utils/filterCategories/filterCategories'
import { Tabs } from 'ui-kit/Tabs/Tabs'

import { OFFER_WIZARD_STEP_IDS } from './constants'
import styles from './IndividualOfferNavigation.module.scss'
import { LabelBooking } from './LabelBooking/LabelBooking'

export const IndividualOfferNavigation = () => {
  const isSplitOfferEnabled = useActiveFeature('WIP_SPLIT_OFFER')
  const { offer } = useIndividualOfferContext()
  const activeStep = useActiveStep(Object.values(OFFER_WIZARD_STEP_IDS))
  const mode = useOfferWizardMode()
  const hasOffer = offer !== null
  const hasPriceCategories = Boolean(
    offer?.priceCategories && offer.priceCategories.length > 0
  )
  const { search } = useLocation()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')

  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  const isEvent = offer?.isEvent || isOfferSubtypeEvent(offerSubtype)

  const steps: StepPattern[] = []

  // First step/tab: informations form or recap
  if (!isSplitOfferEnabled) {
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
  }
  if (isSplitOfferEnabled) {
    steps.push(
      {
        id: OFFER_WIZARD_STEP_IDS.DETAILS,
        label: 'Détails de l’offre',
        path: getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.DETAILS,
          mode,
        }),
        isActive: true,
      },
      {
        id: OFFER_WIZARD_STEP_IDS.ABOUT,
        label: 'Informations pratiques',
        path: getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.ABOUT,
          mode,
        }),
        isActive: true,
      }
    )
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

  // Summary/confirmation steps on creation
  if (mode === OFFER_WIZARD_MODE.CREATION) {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
      }),
      isActive: Boolean(offer?.hasStocks),
    })
  }

  if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    steps.push({
      id: OFFER_WIZARD_STEP_IDS.BOOKINGS,
      label: <LabelBooking bookingsCount={offer?.bookingsCount || 0} />,
      path: getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.BOOKINGS,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
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

  const tabs = stepList.map(({ id, label, url }) => ({
    key: id,
    label,
    url,
  }))

  return (
    <>
      {mode === OFFER_WIZARD_MODE.CREATION ? (
        <Stepper
          activeStep={activeStep}
          steps={stepList}
          className={styles['stepper']}
        />
      ) : (
        <div className={styles['tabs']}>
          <Tabs tabs={tabs} selectedKey={activeStep} />
        </div>
      )}
    </>
  )
}
