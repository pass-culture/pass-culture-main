import React from 'react'
import { useSelector } from 'react-redux'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { computeOffersUrl, OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import { ReactComponent as IcoMiniArrowLeft } from 'icons/ico-mini-arrow-left.svg'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { RootState } from 'store/reducers'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

export interface IActionBarProps {
  onClickNext?: () => void
  onClickPrevious?: () => void
  onClickSaveDraft?: () => void
  step: OFFER_WIZARD_STEP_IDS
}

const ActionBar = ({
  onClickNext,
  onClickPrevious,
  onClickSaveDraft,
  step,
}: IActionBarProps) => {
  const offersSearchFilters = useSelector(
    (state: RootState) => state.offers.searchFilters
  )
  const offersPageNumber = useSelector(
    (state: RootState) => state.offers.pageNumber
  )
  const mode = useOfferWizardMode()
  const backOfferUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)

  const Left = (): JSX.Element => {
    if (mode === OFFER_WIZARD_MODE.CREATION)
      return (
        <>
          {step === OFFER_WIZARD_STEP_IDS.INFORMATIONS ? (
            <ButtonLink
              link={{ to: '/offres', isExternal: false }}
              variant={ButtonVariant.SECONDARY}
            >
              Annuler et quitter
            </ButtonLink>
          ) : (
            <Button
              Icon={IcoMiniArrowLeft}
              onClick={onClickPrevious}
              variant={ButtonVariant.SECONDARY}
            >
              Étape précédente
            </Button>
          )}
        </>
      )
    return (
      <>
        {step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
          <ButtonLink
            link={{ to: backOfferUrl, isExternal: false }}
            variant={ButtonVariant.PRIMARY}
          >
            Retour à la liste des offres
          </ButtonLink>
        ) : (
          <>
            <ButtonLink
              link={{ to: backOfferUrl, isExternal: false }}
              variant={ButtonVariant.SECONDARY}
            >
              Annuler et quitter
            </ButtonLink>
            <Button onClick={onClickNext}>Enregistrer les modifications</Button>
          </>
        )}
      </>
    )
  }

  const Right = (): JSX.Element | null => {
    if (mode !== OFFER_WIZARD_MODE.EDITION)
      return (
        <>
          {step === OFFER_WIZARD_STEP_IDS.SUMMARY ? (
            <>
              <ButtonLink
                link={{ to: '/offres', isExternal: false }}
                variant={ButtonVariant.SECONDARY}
              >
                Sauvegarder le brouillon et quitter
              </ButtonLink>
              <Button onClick={onClickNext}>Publier l'offre</Button>
            </>
          ) : (
            <>
              <Button
                onClick={onClickSaveDraft}
                variant={ButtonVariant.SECONDARY}
              >
                Sauvegarder le brouillon
              </Button>
              <Button
                Icon={IcoMiniArrowRight}
                iconPosition={IconPositionEnum.RIGHT}
                onClick={onClickNext}
              >
                Étape suivante
              </Button>
            </>
          )}
        </>
      )
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
