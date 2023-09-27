import React from 'react'
import { useSelector } from 'react-redux'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullLeftIcon from 'icons/full-left.svg'
import fullRightIcon from 'icons/full-right.svg'
import { RootState } from 'store/reducers'
import { Button, ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface ActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  onClickSaveDraft?: () => void
  isDisabled: boolean
  step: OFFER_WIZARD_STEP_IDS
  offerId?: number
  shouldTrack?: boolean
  submitAsButton?: boolean
}

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  onClickSaveDraft,
  isDisabled,
  step,
  offerId,
  shouldTrack = true,
  submitAsButton = false,
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
  const { logEvent } = useAnalytics()
  const notify = useNotification()

  const logCancel = () => {
    shouldTrack &&
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: step,
        to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft:
          mode === OFFER_WIZARD_MODE.CREATION ||
          mode === OFFER_WIZARD_MODE.DRAFT,
        offerId: offerId,
      })
  }

  const logDraft = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: step,
      to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft:
        mode === OFFER_WIZARD_MODE.CREATION || mode === OFFER_WIZARD_MODE.DRAFT,
      offerId: offerId,
    })
  }

  const Left = (): JSX.Element => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      return (
        <Button
          icon={fullLeftIcon}
          onClick={onClickPrevious}
          variant={ButtonVariant.SECONDARY}
          disabled={isDisabled}
        >
          Étape précédente
        </Button>
      )
    } else if (mode === OFFER_WIZARD_MODE.DRAFT) {
      return (
        <>
          {step === OFFER_WIZARD_STEP_IDS.INFORMATIONS ? (
            <ButtonLink
              link={{ to: '/offres', isExternal: false }}
              variant={ButtonVariant.SECONDARY}
              onClick={logCancel}
            >
              Annuler et quitter
            </ButtonLink>
          ) : (
            <Button
              icon={fullLeftIcon}
              onClick={onClickPrevious}
              variant={ButtonVariant.SECONDARY}
              disabled={isDisabled}
            >
              Étape précédente
            </Button>
          )}
        </>
      )
    } else {
      // mode === OFFER_WIZARD_MODE.EDITION
      return (
        <>
          {step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <ButtonLink
              link={{ to: backOfferUrl, isExternal: false }}
              variant={ButtonVariant.PRIMARY}
              onClick={logCancel}
            >
              Retour à la liste des offres
            </ButtonLink>
          ) : (
            <>
              <ButtonLink
                link={{ to: backOfferUrl, isExternal: false }}
                variant={ButtonVariant.SECONDARY}
                onClick={logCancel}
              >
                Annuler et quitter
              </ButtonLink>
              <SubmitButton
                onClick={onClickNext}
                disabled={isDisabled}
                type={submitAsButton ? 'button' : 'submit'}
              >
                Enregistrer les modifications
              </SubmitButton>
            </>
          )}
        </>
      )
    }
  }

  const Right = (): JSX.Element | null => {
    if (
      mode === OFFER_WIZARD_MODE.CREATION ||
      mode === OFFER_WIZARD_MODE.DRAFT
    ) {
      return (
        <>
          {step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <>
              <ButtonLink
                link={{ to: '/offres', isExternal: false }}
                variant={ButtonVariant.SECONDARY}
                onClick={() => {
                  notify.success(
                    'Brouillon sauvegardé dans la liste des offres'
                  )
                  logDraft()
                }}
              >
                Sauvegarder le brouillon et quitter
              </ButtonLink>
              <Button onClick={onClickNext} disabled={isDisabled}>
                Publier l’offre
              </Button>
            </>
          ) : (
            <>
              <Button
                onClick={onClickSaveDraft}
                disabled={isDisabled}
                variant={ButtonVariant.SECONDARY}
              >
                Sauvegarder le brouillon
              </Button>
              <SubmitButton
                icon={fullRightIcon}
                iconPosition={IconPositionEnum.RIGHT}
                disabled={isDisabled}
                onClick={onClickNext}
              >
                Étape suivante
              </SubmitButton>
            </>
          )}
        </>
      )
    }
    return null
  }

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>{Left()}</ActionsBarSticky.Left>
      <ActionsBarSticky.Right>{Right()}</ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default ActionBar
