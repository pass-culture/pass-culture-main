import { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { OFFER_STATUS_PENDING } from '@/commons/core/Offers/constants'
import { isDateValid } from '@/commons/utils/date'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import fullLinkIcon from '@/icons/full-link.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferConfirmationScreen.module.scss'

interface IndividualOfferConfirmationScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const IndividualOfferConfirmationScreen = ({
  offer,
}: IndividualOfferConfirmationScreenProps): JSX.Element => {
  const isPublishedInTheFuture =
    isDateValid(offer.publicationDate) &&
    new Date() < new Date(offer.publicationDate)
  const isPendingOffer = offer.status === OFFER_STATUS_PENDING
  const queryString = `?structure=${offer.venue.managingOfferer.id}&lieu=${offer.venue.id}`

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
          {isPendingOffer
            ? `Offre en cours de validation`
            : `Offre créée avec succès !`}
        </h2>

        {isPendingOffer && (
          <p className={styles['confirmation-details']}>
            Nous vérifions actuellement l’éligibilité de votre offre.{' '}
            <b>Cette vérification pourra prendre jusqu’à 72h.</b>
            <br />
            <b>Vous ne pouvez pas effectuer de modification pour l’instant.</b>
            <br />
            Vous recevrez un email de confirmation une fois votre offre validée.
          </p>
        )}
      </div>

      {!isPublishedInTheFuture && (
        <div className={styles['display-in-app-link']}>
          <DisplayOfferInAppLink id={offer.id} icon={fullLinkIcon}>
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
