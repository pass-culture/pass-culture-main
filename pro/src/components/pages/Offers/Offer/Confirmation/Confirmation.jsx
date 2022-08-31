import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import Spinner from 'components/layout/Spinner'
import { ReactComponent as PendingIcon } from 'components/pages/Offers/Offer/Confirmation/assets/pending.svg'
import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_PENDING } from 'core/Offers/constants'
import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { ButtonLink } from 'ui-kit'
import { WEBAPP_URL } from 'utils/config'

const Confirmation = ({ offer, setOffer, reloadOffer }) => {
  const [isLoading, setIsLoading] = useState(true)
  const { logEvent } = useAnalytics()
  const resetOffer = useCallback(() => {
    setOffer(null)
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.CONFIRMATION,
      to: OfferBreadcrumbStep.DETAILS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_BUTTON_NEW_OFFER,
      isEdition: false,
    })
  }, [setOffer])

  useEffect(() => {
    reloadOffer()
    setIsLoading(false)
  }, [])

  const offerPreviewUrl = `${WEBAPP_URL}/offre/${offer.nonHumanizedId}`

  const openWindow = useCallback(
    event => {
      event.preventDefault()

      window
        .open(
          offerPreviewUrl,
          'targetWindow',
          'toolbar=no, width=375, height=667'
        )
        ?.focus()

      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OfferBreadcrumbStep.CONFIRMATION,
        to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
        used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_PREVIEW,
        isEdition: false,
      })
    },
    [offerPreviewUrl]
  )

  if (isLoading) return <Spinner />

  const isPendingOffer = offer.status === OFFER_STATUS_PENDING

  let queryString = `?structure=${offer.venue.managingOfferer.id}&lieu=${offer.venueId}`

  return (
    <div className="offer-confirmation">
      {isPendingOffer ? (
        <div>
          <PendingIcon className="oc-pending" />
          <h2 className="oc-title">Offre en cours de validation</h2>
          <p className="oc-details">
            Votre offre est en cours de validation par l’équipe pass Culture.
            Nous vérifions actuellement son éligibilité.
            <b> Cette vérification pourra prendre jusqu’à 72h.</b> Vous recevrez
            un e-mail de confirmation une fois votre offre validée et disponible
            à la réservation.
          </p>
        </div>
      ) : (
        <div>
          <ValidateIcon className="oc-validate" />
          <h2 className="oc-title">Offre publiée !</h2>
          <p className="oc-details">
            Votre offre est désormais disponible à la réservation sur
            l’application pass Culture.
          </p>
        </div>
      )}
      <div className="display-in-app-link">
        <ButtonLink
          link={{ to: offerPreviewUrl, isExternal: true }}
          className={'kikou'}
          Icon={LinkIcon}
          onClick={openWindow}
        >
          Visualiser l’offre dans l’application
        </ButtonLink>
      </div>
      <div className="oc-actions">
        <Link
          className="secondary-link"
          onClick={resetOffer}
          to={`/offre/creation/individuel${queryString}`}
        >
          Créer une nouvelle offre
        </Link>
        <Link
          className="primary-link"
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OfferBreadcrumbStep.CONFIRMATION,
              to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
              used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_BUTTON_OFFER_LIST,
              isEdition: false,
            })
          }
          to={`/offres`}
        >
          Voir la liste des offres
        </Link>
      </div>
    </div>
  )
}

Confirmation.propTypes = {
  offer: PropTypes.shape().isRequired,
  setOffer: PropTypes.func.isRequired,
}

export default Confirmation
