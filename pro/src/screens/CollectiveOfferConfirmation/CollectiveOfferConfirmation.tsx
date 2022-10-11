import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { ReactComponent as PendingIcon } from 'components/pages/Offers/Offer/Confirmation/assets/pending.svg'
import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import { Banner, Title } from 'ui-kit'

import styles from './CollectiveOfferConfirmation.module.scss'

interface ICollectiveOfferConfirmationProps {
  offererId?: string | null
  offerStatus?: OfferStatus
  isShowcase?: boolean
  institutionDisplayName?: string
}

const activeOffer = (institutionDisplayName?: string) => ({
  title: 'Offre créée avec succès !',
  description: (
    <>
      Votre offre est désormais disponible sur <b>ADAGE</b> (L'Application
      Dédiée À la Généralisation de l’Éducation artistique et culturelle) et{' '}
      {institutionDisplayName ? (
        <>
          <b>visible uniquement</b> par :
          <br />
          <br />
          <br />
          <b>{institutionDisplayName}</b>
        </>
      ) : (
        <>visible par les enseignants et chefs d’établissement.</>
      )}
    </>
  ),
  Icon: ValidateIcon,
})

const pendingOffer = {
  title: 'Offre en cours de validation !',
  description: (
    <>
      Votre offre est en cours de validation par l’équipe pass Culture, nous
      vérifions actuellement son éligibilité. Cette vérification pourra prendre
      jusqu’à 72h.
    </>
  ),
  Icon: PendingIcon,
}

const showcaseOffer = {
  title: 'Offre créée avec succès !',
  description: (
    <>
      Votre offre est désormais disponible sur <b>ADAGE</b> (L’Application
      Dédiée À la Généralisation de l’Éducation artistique et culturelle) et
      visible par les enseignants et chefs d’établissement. Vous aurez la
      possibilité de revenir <b>éditer</b> votre offre et
      <b> compléter</b> les éléments de date(s) et prix.
    </>
  ),
  Icon: ValidateIcon,
}

const mapOfferStatusToData = (
  status?: OfferStatus,
  isShowcase?: boolean,
  institutionName?: string
) => {
  if (status === OfferStatus.PENDING) {
    return pendingOffer
  }

  if (isShowcase) {
    return showcaseOffer
  }

  return activeOffer(institutionName)
}

const CollectiveOfferConfirmation = ({
  offererId,
  offerStatus,
  isShowcase,
  institutionDisplayName,
}: ICollectiveOfferConfirmationProps): JSX.Element => {
  const { title, description, Icon } = mapOfferStatusToData(
    offerStatus,
    isShowcase,
    institutionDisplayName
  )

  return (
    <div className={styles['confirmation-wrapper']}>
      <div className={styles['confirmation']}>
        <Icon className={styles['confirmation-icon']} />
        <div className={styles['confirmation-section']}>
          <div className={styles['confirmation-section-header']}>
            <Title as="h2" level={3}>
              {title}
            </Title>
          </div>
          <p className={styles['form-layout-section-description']}>
            {description}
          </p>
        </div>
        <div className={styles['confirmation-actions']}>
          <Link
            className={cn(styles['confirmation-action'], 'secondary-link')}
            to="/offres/collectives"
          >
            Voir mes offres
          </Link>
          <Link
            className={cn('primary-button', styles['confirmation-action'])}
            to={`/offre/creation${offererId ? `?structure=${offererId}` : ''}`}
          >
            Créer une nouvelle offre
          </Link>
        </div>
      </div>
      <Banner
        type="notification-info"
        className={styles['confirmation-banner']}
      >
        <h2 className={styles['confirmation-banner-title']}>
          Quelle est la prochaine étape ?
        </h2>
        {isShowcase ? (
          <>
            L’enseignant doit préréserver votre offre depuis son compte ADAGE.
            <br />
            Une fois la préréservation faite, vous verrez une réservation
            portant le statut préréservé.
          </>
        ) : (
          <>
            Les enseignants intéressés par votre offre vitrine vous contacterons
            par mail ou téléphone. <br />
            Après un accord mutuel, vous pourrez créer une offre réservable en
            complétant la date, le prix et l’établissement convenus avec
            l’enseignant. <br />
            Cette nouvelle offre apparaitra sur ADAGE et pourra être
            pré-réservée par l’enseignant.
          </>
        )}
      </Banner>
    </div>
  )
}

export default CollectiveOfferConfirmation
