import React from 'react'
import { useSelector } from 'react-redux'

import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { computeOffersUrl } from 'core/Offers'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { RootState } from 'store/reducers'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IActionsFormV2Props {
  isCreation: boolean
  offerId: string
  className?: string
  publishOffer: () => void
  disablePublish: boolean
}

const ActionsFormV2 = ({
  offerId,
  className,
  publishOffer,
  isCreation = false,
  disablePublish = false,
}: IActionsFormV2Props): JSX.Element => {
  const logEvent = useSelector((state: RootState) => state.app.logEvent)

  const renderCreationActions = (): JSX.Element => (
    <div className={className}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        link={{
          to: `/offre/${offerId}/individuel/creation/stocks`,
          isExternal: false,
        }}
        onClick={() =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OfferBreadcrumbStep.SUMMARY,
            to: OfferBreadcrumbStep.STOCKS,
            used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
            isEdition: !isCreation,
          })
        }
      >
        Étape précédente
      </ButtonLink>
      <Button
        variant={ButtonVariant.PRIMARY}
        onClick={publishOffer}
        disabled={disablePublish}
      >
        Publier l'offre
      </Button>
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
            })
          }
        >
          Retour à la liste des offres
        </ButtonLink>
      </div>
    )
  }

  return isCreation ? renderCreationActions() : renderEditionActions()
}

export default ActionsFormV2
