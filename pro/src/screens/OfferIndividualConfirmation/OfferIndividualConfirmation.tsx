import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_PENDING } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as FullLink } from 'icons/full-link.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { ReactComponent as PendingIcon } from 'icons/pending.svg'
import { DisplayOfferInAppLink } from 'screens/OfferIndividual/Summary/DisplayOfferInAppLink'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OfferIndividualConfirmation.module.scss'

interface IOfferIndividualConfirmationProps {
  offer: IOfferIndividual
}

const OfferIndividualConfirmation = ({
  offer,
}: IOfferIndividualConfirmationProps): JSX.Element => {
  const isPendingOffer = offer.status === OFFER_STATUS_PENDING
  const queryString = `?structure=${offer.venue.offerer.nonHumanizedId}&lieu=${offer.venueId}`
  const { logEvent } = useAnalytics()
  const title = isPendingOffer
    ? 'Offre en cours de validation'
    : 'Offre publiée !'
  return (
    <div className={styles['confirmation-container']}>
      <div>
        {isPendingOffer ? (
          <PendingIcon className={styles['pending-icon']} />
        ) : (
          <SvgIcon
            src={fullValidateIcon}
            alt=""
            className={styles['validate-icon']}
          />
        )}
        <h2 className={styles['confirmation-title']}>{title}</h2>
        {isPendingOffer ? (
          <p className={styles['confirmation-details']}>
            Votre offre est en cours de validation par l’équipe pass Culture.
            Nous vérifions actuellement son éligibilité.
            <b>
              {' '}
              Cette vérification pourra prendre jusqu’à 72h. Vous ne pouvez pas
              effectuer de modification pour l’instant.{' '}
            </b>
            Vous recevrez un email de confirmation une fois votre offre validée
            et disponible à la réservation.
          </p>
        ) : (
          <p className={styles['confirmation-details']}>
            Votre offre est désormais disponible à la réservation sur
            l’application pass Culture.
          </p>
        )}
      </div>
      <div className={styles['display-in-app-link']}>
        <DisplayOfferInAppLink
          nonHumanizedId={offer.nonHumanizedId}
          tracking={{
            isTracked: true,
            trackingFunction: () =>
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
                to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
                used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_PREVIEW,
                isEdition: false,
              }),
          }}
          text="Visualiser l’offre dans l’application"
          Icon={FullLink}
        />
      </div>
      <div className={styles['confirmation-actions']}>
        <ButtonLink
          link={{
            to: '/offre/creation' + queryString,
            isExternal: true,
          }}
          variant={ButtonVariant.SECONDARY}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              to: OFFER_FORM_HOMEPAGE,
              used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_BUTTON_NEW_OFFER,
              isEdition: false,
            })
          }
        >
          Créer une nouvelle offre
        </ButtonLink>
        <ButtonLink
          link={{
            to: `/offres`,
            isExternal: false,
          }}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              to: OFFER_FORM_NAVIGATION_OUT.OFFERS,
              used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_BUTTON_OFFER_LIST,
              isEdition: false,
            })
          }
          variant={ButtonVariant.PRIMARY}
        >
          Voir la liste des offres
        </ButtonLink>
      </div>
    </div>
  )
}

export default OfferIndividualConfirmation
