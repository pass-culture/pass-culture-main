import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
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
  isDisabled: boolean
  step: OFFER_WIZARD_STEP_IDS
  dirtyForm?: boolean
}

export const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
  step,
  dirtyForm,
}: ActionBarProps) => {
  const mode = useOfferWizardMode()
  const backOfferUrl = computeOffersUrl({})
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

    // mode === OFFER_WIZARD_MODE.EDITION
    return step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
      <ButtonLink
        link={{ to: backOfferUrl, isExternal: false }}
        variant={ButtonVariant.PRIMARY}
      >
        Retour à la liste des offres
      </ButtonLink>
    ) : (
      <>
        <Button onClick={onClickPrevious} variant={ButtonVariant.SECONDARY}>
          Annuler et quitter
        </Button>

        <Button type="submit" onClick={onClickNext} disabled={isDisabled}>
          Enregistrer les modifications
        </Button>
      </>
    )
  }

  const Right = (): JSX.Element | null => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
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
          {step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <>
              <ButtonLink
                link={{ to: '/offres', isExternal: false }}
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  notify.success(
                    'Brouillon sauvegardé dans la liste des offres'
                  )
                }}
              >
                Sauvegarder le brouillon et quitter
              </ButtonLink>

              <Button type="submit" disabled={isDisabled}>
                Publier l’offre
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
    <ActionsBarSticky>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right
        inverseWhenSmallerThanTablet={step === OFFER_WIZARD_STEP_IDS.SUMMARY}
      >
        {Right()}
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
