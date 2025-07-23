import { useLocation } from 'react-router'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { computeIndividualOffersUrl } from 'commons/core/Offers/utils/computeIndividualOffersUrl'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ActionBar.module.scss'

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
  const notify = useNotification()

  const Left = (): JSX.Element => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
        <Button
          icon={fullLeftIcon}
          onClick={onClickPrevious}
          variant={ButtonVariant.SECONDARY}
          disabled={isDisabled}
        >
          Retour
        </Button>
      )
    }

    if (
      mode === OFFER_WIZARD_MODE.EDITION &&
      step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS &&
      isEvent
    ) {
      return (
        <Button onClick={onClickPrevious} variant={ButtonVariant.SECONDARY}>
          Quitter le mode édition
        </Button>
      )
    }

    // mode === OFFER_WIZARD_MODE.EDITION
    return step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY ? (
      <ButtonLink to={backOfferUrl} variant={ButtonVariant.PRIMARY}>
        Retour à la liste des offres
      </ButtonLink>
    ) : (
      <>
        <Button onClick={onClickPrevious} variant={ButtonVariant.SECONDARY}>
          Annuler et quitter
        </Button>

        <Button
          type="submit"
          onClick={onClickNext}
          disabled={isDisabled}
          ref={saveEditionChangesButtonRef}
        >
          Enregistrer les modifications
        </Button>
      </>
    )
  }

  const Right = (): JSX.Element | null => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
        <>
          {!isDisabled && (
            <>
              {dirtyForm === false && (
                <span className={styles['draft-indicator']}>
                  <SvgIcon
                    src={fullValidateIcon}
                    alt=""
                    width="16"
                    className={styles['draft-saved-icon']}
                  />
                  Brouillon enregistré
                </span>
              )}
              {dirtyForm === true && (
                <span className={styles['draft-indicator']}>
                  <div className={styles['draft-not-saved-icon']} />
                  Brouillon non enregistré
                </span>
              )}
            </>
          )}

          {step === INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <>
              {!isDisabled && (
                <ButtonLink
                  to={isOnboarding ? '/accueil' : '/offres'}
                  variant={ButtonVariant.SECONDARY}
                  onClick={() => {
                    notify.success(
                      'Brouillon sauvegardé dans la liste des offres'
                    )
                  }}
                >
                  Sauvegarder le brouillon et quitter
                </ButtonLink>
              )}

              <Button type="submit" disabled={isDisabled}>
                {publicationMode === 'later'
                  ? 'Programmer l’offre'
                  : 'Publier l’offre'}
              </Button>
            </>
          ) : (
            <Button
              type="submit"
              icon={fullRightIcon}
              iconPosition={IconPositionEnum.RIGHT}
              disabled={isDisabled}
              onClick={onClickNext}
            >
              Enregistrer et continuer
            </Button>
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
