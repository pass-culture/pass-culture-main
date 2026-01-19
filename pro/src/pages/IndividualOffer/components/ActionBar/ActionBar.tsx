import { useLocation } from 'react-router'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullLeftIcon from '@/icons/full-left.svg'
import fullRightIcon from '@/icons/full-right.svg'

import { ActionBarDraftStatus } from './ActionBarDraftStatus/ActionBarDraftStatus'

export interface ActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  isDisabled?: boolean
  publicationMode?: 'later' | 'now'
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  dirtyForm?: boolean
  saveEditionChangesButtonRef?: React.RefObject<HTMLButtonElement>
  isEvent?: boolean
}

export const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled = false,
  publicationMode = 'now',
  step,
  dirtyForm,
  saveEditionChangesButtonRef,
  isEvent = false,
}: ActionBarProps) => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()
  const backOfferUrl = computeIndividualOffersUrl({})
  const snackBar = useSnackBar()

  const Left = (): JSX.Element => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
        <Button
          icon={fullLeftIcon}
          onClick={onClickPrevious}
          variant={ButtonVariant.SECONDARY}
          disabled={isDisabled}
          label="Retour"
        />
      )
    }

    if (
      mode === OFFER_WIZARD_MODE.EDITION &&
      step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE &&
      isEvent
    ) {
      return (
        <Button
          onClick={onClickPrevious}
          variant={ButtonVariant.SECONDARY}
          label="Quitter le mode édition"
        />
      )
    }

    // mode === OFFER_WIZARD_MODE.EDITION
    return step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY ? (
      <Button as="a" to={backOfferUrl} label="Retour à la liste des offres" />
    ) : (
      <>
        <Button
          onClick={onClickPrevious}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          label="Annuler et quitter"
        />

        <Button
          type="submit"
          onClick={onClickNext}
          disabled={isDisabled}
          ref={saveEditionChangesButtonRef}
          label="Enregistrer les modifications"
        />
      </>
    )
  }

  const Right = (): JSX.Element | null => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
        <>
          {!isDisabled && dirtyForm !== undefined && (
            <ActionBarDraftStatus isSaved={dirtyForm === false} />
          )}

          {step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <>
              {!isDisabled && (
                <Button
                  as="a"
                  to={isOnboarding ? '/accueil' : '/offres'}
                  variant={ButtonVariant.SECONDARY}
                  onClick={() => {
                    snackBar.success(
                      'Brouillon sauvegardé dans la liste des offres'
                    )
                  }}
                  label="Sauvegarder le brouillon et quitter"
                />
              )}

              <Button
                type="submit"
                disabled={isDisabled}
                label={
                  publicationMode === 'later'
                    ? 'Programmer l’offre'
                    : 'Publier l’offre'
                }
              />
            </>
          ) : (
            <Button
              type="submit"
              icon={fullRightIcon}
              iconPosition={IconPositionEnum.RIGHT}
              disabled={isDisabled}
              onClick={onClickNext}
              ref={saveEditionChangesButtonRef}
              label="Enregistrer et continuer"
            />
          )}
        </>
      )
    }

    return null
  }

  return (
    <ActionsBarSticky hasSideNav={!isOnboarding}>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right
        inverseWhenSmallerThanTablet={
          step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY
        }
      >
        {Right()}
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
