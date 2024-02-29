import { useSelector } from 'react-redux'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { RootState } from 'store/rootReducer'
import { Button, ButtonLink, SubmitButton } from 'ui-kit'
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

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  isDisabled,
  step,
  dirtyForm,
}: ActionBarProps) => {
  const offersSearchFilters = useSelector(
    (state: RootState) => state.offers.searchFilters
  )
  const offersPageNumber = useSelector(
    (state: RootState) => state.offers.pageNumber
  )
  const mode = useOfferWizardMode()
  const backOfferUrl = computeOffersUrl({
    ...offersSearchFilters,
    page: offersPageNumber,
  })
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

        <SubmitButton onClick={onClickNext} disabled={isDisabled}>
          Enregistrer les modifications
        </SubmitButton>
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
              <Button onClick={onClickNext} disabled={isDisabled}>
                Publier l’offre
              </Button>
            </>
          ) : (
            <SubmitButton
              icon={fullRightIcon}
              iconPosition={IconPositionEnum.RIGHT}
              disabled={isDisabled}
              onClick={onClickNext}
            >
              Enregistrer et continuer
            </SubmitButton>
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

export default ActionBar
