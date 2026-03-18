import { useLocation } from 'react-router'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'

import { ActionBarLeft } from './ActionBarLeft'
import { ActionBarRight } from './ActionBarRight'

export interface ActionBarProps {
  dirtyForm?: boolean
  isDisabled?: boolean
  isEvent?: boolean
  onClickNext?: () => void
  onClickPrevious?: () => void
  publicationMode?: 'later' | 'now'
  saveEditionChangesButtonRef?: React.RefObject<HTMLButtonElement | null>
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
}

export const ActionBar = ({
  dirtyForm,
  onClickNext,
  onClickPrevious,
  isDisabled = false,
  isEvent = false,
  publicationMode = 'now',
  saveEditionChangesButtonRef,
  step,
}: ActionBarProps) => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()

  return (
    <ActionsBarSticky hasSideNav={!isOnboarding}>
      <ActionsBarSticky.Left>
        <ActionBarLeft
          isDisabled={isDisabled}
          isEvent={isEvent}
          mode={mode}
          onClickNext={onClickNext}
          onClickPrevious={onClickPrevious}
          publicationMode={publicationMode}
          saveEditionChangesButtonRef={saveEditionChangesButtonRef}
          step={step}
        />
      </ActionsBarSticky.Left>

      {mode === OFFER_WIZARD_MODE.CREATION && (
        <ActionsBarSticky.Right
          inverseWhenSmallerThanTablet={
            step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY
          }
        >
          <ActionBarRight
            dirtyForm={dirtyForm}
            onClickNext={onClickNext}
            onClickPrevious={onClickPrevious}
            isOnboarding={isOnboarding}
            isDisabled={isDisabled}
            publicationMode={publicationMode}
            saveEditionChangesButtonRef={saveEditionChangesButtonRef}
            step={step}
          />
        </ActionsBarSticky.Right>
      )}
    </ActionsBarSticky>
  )
}
