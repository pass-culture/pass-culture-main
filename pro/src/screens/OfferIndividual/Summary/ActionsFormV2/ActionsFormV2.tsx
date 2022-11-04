/* istanbul ignore file: will be removed on offer v3 */
import cn from 'classnames'
import React from 'react'
import { useSelector } from 'react-redux'

import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { computeOffersUrl, OFFER_WIZARD_MODE } from 'core/Offers'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import {
  searchFiltersSelector,
  searchPageNumberSelector,
} from 'store/offers/selectors'
import { RootState } from 'store/reducers'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ActionsFormsV2.module.scss'

interface IActionsFormV2Props {
  offerId: string
  className?: string
  publishOffer: () => void
  disablePublish: boolean
}

const ActionsFormV2 = ({
  offerId,
  className,
  publishOffer,
  disablePublish = false,
}: IActionsFormV2Props): JSX.Element => {
  const { logEvent } = useAnalytics()
  const offersSearchFilters = useSelector(searchFiltersSelector)
  const offersPageNumber = useSelector(searchPageNumberSelector)
  const quitUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)
  const notification = useNotification()
  const isDraftEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')
  const mode = useOfferWizardMode()
  const backOfferUrl = {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuel/creation/stocks`,
    [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/stocks`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/${offerId}/individuel/stocks`,
  }[mode]

  const renderCreationActions = (): JSX.Element => (
    <div className={cn(className, styles['draft-actions'])}>
      <div>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            to: backOfferUrl,
            isExternal: false,
          }}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OfferBreadcrumbStep.SUMMARY,
              to: OfferBreadcrumbStep.STOCKS,
              used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
              isDraft: true,
              offerId: offerId,
              isEdition: mode === OFFER_WIZARD_MODE.EDITION,
            })
          }
        >
          Étape précédente
        </ButtonLink>
      </div>
      <div className={styles['actions-last']}>
        {isDraftEnabled && (
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{ to: quitUrl, isExternal: false }}
            onClick={() => {
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OfferBreadcrumbStep.SUMMARY,
                to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
                used: OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS,
                isEdition: mode === OFFER_WIZARD_MODE.EDITION,
                isDraft: true,
                offerId: offerId,
              })
              notification.success(
                'Brouillon sauvegardé dans la liste des offres'
              )
            }}
          >
            Sauvegarder le brouillon et quitter
          </ButtonLink>
        )}
        <Button
          variant={ButtonVariant.PRIMARY}
          onClick={publishOffer}
          disabled={disablePublish}
        >
          Publier l'offre
        </Button>
      </div>
    </div>
  )

  const renderEditionActions = (): JSX.Element => {
    const offersSearchFilters = useSelector(
      (state: RootState) => state.offers.searchFilters
    )
    const offersPageNumber = useSelector(
      (state: RootState) => state.offers.pageNumber
    )
    const backOfferUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)

    return (
      <div className={className}>
        <ButtonLink
          variant={ButtonVariant.PRIMARY}
          link={{ to: backOfferUrl, isExternal: false }}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OfferBreadcrumbStep.SUMMARY,
              to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
              used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
              isEdition: mode === OFFER_WIZARD_MODE.EDITION,
              isDraft: mode === OFFER_WIZARD_MODE.DRAFT,
              offerId: offerId,
            })
          }
        >
          Retour à la liste des offres
        </ButtonLink>
      </div>
    )
  }

  return mode === OFFER_WIZARD_MODE.EDITION
    ? renderEditionActions()
    : renderCreationActions()
}

export default ActionsFormV2
