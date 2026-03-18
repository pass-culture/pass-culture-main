import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullRightIcon from '@/icons/full-right.svg'

import { ActionBarDraftStatus } from './ActionBarDraftStatus/ActionBarDraftStatus'

interface ActionBarRightProps {
  dirtyForm: boolean | undefined
  isDisabled: boolean
  isOnboarding: boolean
  onClickNext?: () => void
  onClickPrevious?: () => void
  publicationMode?: 'later' | 'now'
  saveEditionChangesButtonRef?: React.RefObject<HTMLButtonElement | null>
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
}

export const ActionBarRight = ({
  dirtyForm,
  isDisabled,
  isOnboarding,
  onClickNext,
  publicationMode,
  saveEditionChangesButtonRef,
  step,
}: Readonly<ActionBarRightProps>) => {
  const snackBar = useSnackBar()

  return (
    <>
      {!isDisabled && dirtyForm !== undefined && (
        <ActionBarDraftStatus isSaved={!dirtyForm} />
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
