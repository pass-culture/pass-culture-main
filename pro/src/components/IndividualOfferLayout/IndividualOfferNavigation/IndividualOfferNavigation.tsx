import { FC } from 'react'
import { generatePath, useLocation } from 'react-router'

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { Step, StepPattern, Stepper } from '@/components/Stepper/Stepper'
import {
  getOfferSubtypeFromParam,
  isOfferSubtypeEvent,
} from '@/pages/IndividualOffer/commons/filterCategories'
import { NavLinkItems } from '@/ui-kit/NavLinkItems/NavLinkItems'

import styles from './IndividualOfferNavigation.module.scss'
import { LabelBooking } from './LabelBooking/LabelBooking'
import { getSteps } from './utils/getSteps'
import { getLastSubmittedStep } from './utils/handleLastSubmittedStep'

export const IndividualOfferNavigation = () => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { offer, isEvent } = useIndividualOfferContext()
  const activeStep = useActiveStep(
    Object.values(INDIVIDUAL_OFFER_WIZARD_STEP_IDS)
  )
  const isMediaPageFeatureEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )
  const mode = useOfferWizardMode()

  const { search } = useLocation()
  const queryParams = new URLSearchParams(search)
  const queryOfferType = queryParams.get('offer-type')
  const offerSubtype = getOfferSubtypeFromParam(queryOfferType)
  // TODO (igabriele, 2025-08-04): Confusing and error-prone. We should have a single source of truth for `isEvent`.
  const isSurelyAnEvent =
    isEvent || offer?.isEvent || isOfferSubtypeEvent(offerSubtype)

  const steps = getSteps({
    isMediaPageFeatureEnabled,
    isNewOfferCreationFlowFeatureActive,
    isEvent: isSurelyAnEvent,
    mode,
    bookingsCount: offer?.bookingsCount,
  })

  const lastSubmittedStep = getLastSubmittedStep(offer?.id)
  const lastSubmittedStepIndex = steps.findIndex(
    (s) => lastSubmittedStep === s.id
  )

  const stepList = steps.map(
    ({ id, label }: StepPattern, stepIndex: number): Step => {
      const step: Step = { id, label }
      const canBeClicked =
        offer &&
        (mode !== OFFER_WIZARD_MODE.CREATION ||
          lastSubmittedStepIndex >= stepIndex)

      if (canBeClicked) {
        step.url = generatePath(
          getIndividualOfferPath({
            step: step.id,
            mode,
            isOnboarding,
          }),
          {
            offerId: offer.id,
          }
        )
      }

      return step
    }
  )

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
          <NavLinkItems
            navLabel="Sous menu - offre individuelle"
            links={stepList.map(({ id, label, url }) => ({
              key: id,
              label,
              url: url || '#',
            }))}
            selectedKey={activeStep}
          />
        </div>
      )}
    </>
  )
}
