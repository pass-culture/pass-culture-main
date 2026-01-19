import {
  type GetIndividualOfferResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isDateValid } from '@/commons/utils/date'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
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
  const isPendingOffer = offer.status === OfferStatus.PENDING

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
        <Button
          as="a"
          to={getIndividualOfferUrl({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
            mode: OFFER_WIZARD_MODE.CREATION,
            isOnboarding: false,
          })}
          isExternal
          variant={ButtonVariant.SECONDARY}
          label="Créer une nouvelle offre"
        />

        <Button as="a" to="/offres" label="Voir la liste des offres" />
      </div>
    </div>
  )
}
