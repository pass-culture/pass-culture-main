import cn from 'classnames'
import React from 'react'
import { useSelector } from 'react-redux'

import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { computeOffersUrl } from 'core/Offers'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import {
  searchFiltersSelector,
  searchPageNumberSelector,
} from 'store/offers/selectors'
import { RootState } from 'store/reducers'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ActionsFormsV2.module.scss'

interface IActionsFormV2Props {
  isCreation: boolean
  isDraft: boolean
  offerId: string
  className?: string
  publishOffer: () => void
  disablePublish: boolean
}

const ActionsFormV2 = ({
  offerId,
  className,
  publishOffer,
  isCreation,
  isDraft,
  disablePublish = false,
}: IActionsFormV2Props): JSX.Element => {
  const { logEvent } = useAnalytics()
  const offersSearchFilters = useSelector(searchFiltersSelector)
  const offersPageNumber = useSelector(searchPageNumberSelector)
  const quitUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)
  const notification = useNotification()
  const isDraftEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')
  let backOfferUrl = `/offre/${offerId}/individuel/creation/stocks`
  if (isDraft) backOfferUrl = `/offre/${offerId}/individuel/brouillon/stocks`

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
              isEdition: !isCreation,
              isDraft: true,
              offerId: offerId,
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
                isEdition: !isCreation,
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
              isEdition: !isCreation,
              isDraft: isDraft || isCreation,
              offerId: offerId,
            })
          }
        >
          Retour à la liste des offres
        </ButtonLink>
      </div>
    )
  }

  return isCreation || isDraft
    ? renderCreationActions()
    : renderEditionActions()
}

export default ActionsFormV2
