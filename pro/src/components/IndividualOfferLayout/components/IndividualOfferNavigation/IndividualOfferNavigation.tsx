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
import { type StepItem, Stepper } from '@/design-system/Stepper/Stepper'
import { Tabs } from '@/ui-kit/Tabs/Tabs'

import styles from './IndividualOfferNavigation.module.scss'
import { getSteps, type StepPattern } from './utils/getSteps'

export const IndividualOfferNavigation = () => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')
  const { offer, isEvent } = useIndividualOfferContext()
  const activeStep = useActiveStep(
    Object.values(INDIVIDUAL_OFFER_WIZARD_STEP_IDS)
  )

  const mode = useOfferWizardMode()

  const steps = getSteps({
    isEvent,
    mode,
    bookingsCount: offer?.bookingsCount,
    isOfferExposureEnabled,
  })

  const stepList = steps.map(
    ({ id, label }: StepPattern): StepItem => ({
      id,
      label,
      url: offer
        ? generatePath(
            getIndividualOfferPath({
              step: id,
              mode,
              isOnboarding,
              isOfferExposureEnabled,
            }),
            {
              offerId: offer.id.toString(),
            }
          )
        : undefined,
    })
  )

  return (
    <>
      {mode === OFFER_WIZARD_MODE.CREATION ? (
        <div className={styles['stepper-wrapper']}>
          <Stepper activeStep={activeStep} steps={stepList} />
        </div>
      ) : (
        <div className={styles.tabs}>
          <Tabs
            type="links"
            navLabel="Sous menu - offre individuelle"
            items={stepList.map(({ id, label, url }) => ({
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
