import { useSelector } from 'react-redux'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_PENDING } from 'core/Offers/constants'
import fullLinkIcon from 'icons/full-link.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { DisplayOfferInAppLink } from 'screens/IndividualOffer/SummaryScreen/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { selectCurrentOffererId } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatDateTimeParts, isDateValid } from 'utils/date'

import styles from './IndividualOfferConfirmationScreen.module.scss'

interface IndividualOfferConfirmationScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const IndividualOfferConfirmationScreen = ({
  offer,
}: IndividualOfferConfirmationScreenProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const isPublishedInTheFuture = isDateValid(offer.publicationDate)
  const isPendingOffer = offer.status === OFFER_STATUS_PENDING
  const queryString = `?structure=${offer.venue.managingOfferer.id}&lieu=${offer.venue.id}`
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { date: publicationDate, time: publicationTime } = formatDateTimeParts(
    offer.publicationDate
  )

  return (
    <div className={styles['confirmation-container']}>
      <div>
        {isPendingOffer ? (
          <SvgIcon
            src={fullWaitIcon}
            alt=""
            className={styles['pending-icon']}
          />
        ) : (
          <SvgIcon
            src={fullValidateIcon}
            alt=""
            className={styles['validate-icon']}
          />
        )}
        <h2 className={styles['confirmation-title']}>
          {isPublishedInTheFuture
            ? isPendingOffer
              ? `Offre programmée en cours de validation`
              : `Offre programmée !`
            : isPendingOffer
              ? `Offre en cours de validation`
              : `Offre publiée !`}
        </h2>

        {isPendingOffer ? (
          <p className={styles['confirmation-details']}>
            Nous vérifions actuellement l’éligibilité de votre offre.{' '}
            <b>Cette vérification pourra prendre jusqu’à 72h.</b>
            <br />
            <b>Vous ne pouvez pas effectuer de modification pour l’instant.</b>
            <br />
            {isPublishedInTheFuture ? (
              <>
                <>
                  Vous recevrez un email de confirmation une fois votre offre{' '}
                  validée.
                </>
                <br />
                <>
                  Elle sera automatiquement publiée le {publicationDate} à{' '}
                  {publicationTime}.
                </>
              </>
            ) : (
              'Vous recevrez un email de confirmation une fois votre offre validée et disponible à la réservation.'
            )}
          </p>
        ) : (
          <p className={styles['confirmation-details']}>
            {isPublishedInTheFuture
              ? `Votre offre sera disponible à la réservation sur l’application pass Culture le ${publicationDate} à ${publicationTime}.`
              : 'Votre offre est désormais disponible à la réservation sur l’application pass Culture.'}
          </p>
        )}
      </div>

      {!isPublishedInTheFuture && (
        <div className={styles['display-in-app-link']}>
          <DisplayOfferInAppLink
            id={offer.id}
            icon={fullLinkIcon}
            onClick={() => {
              logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
                to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
                used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_PREVIEW,
                isEdition: false,
                offerId: offer.id,
                offerType: 'individual',
                offererId: selectedOffererId?.toString(),
              })
            }}
          >
            Visualiser l’offre dans l’application
          </DisplayOfferInAppLink>
        </div>
      )}

      <div className={styles['confirmation-actions']}>
        <ButtonLink
          to={`/offre/creation${queryString}`}
          isExternal
          className={styles['confirmation-action']}
          variant={ButtonVariant.SECONDARY}
        >
          Créer une nouvelle offre
        </ButtonLink>

        <ButtonLink
          to="/offres"
          className={styles['confirmation-action']}
          variant={ButtonVariant.PRIMARY}
        >
          Voir la liste des offres
        </ButtonLink>
      </div>
    </div>
  )
}
