import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as PendingIcon } from 'components/pages/Offers/Offer/Confirmation/assets/pending.svg'
import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import { OfferStatus } from 'custom_types/offer'
import { Title } from 'ui-kit'

import styles from './OfferEducationalConfirmation.module.scss'

interface IOfferEducationalConfirmationProps {
  offererId?: string | null
  offerStatus?: OfferStatus
  isShowcase?: boolean
}

const activeOffer = {
  title: 'Offre créée avec succès !',
  description: (
    <>
      Votre offre est désormais disponible sur <b>ADAGE</b> (L'Application
      Dédiée À la Généralisation de l’Éducation artistique et culturelle) et
      visible par les enseignants et chefs d’établissement de l’Éducation
      nationale.
    </>
  ),
  Icon: ValidateIcon,
}

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
      visible par les enseignants et chefs d’établissement de l’Éducation
      nationale. Vous aurez la possibilité de revenir <b>éditer</b> votre offre
      et
      <b> compléter</b> les éléments de date(s) et prix.
    </>
  ),
  Icon: ValidateIcon,
}

const mapOfferStatusToData = (status?: OfferStatus, isShowcase?: boolean) => {
  if (status === OfferStatus.OFFER_STATUS_PENDING) {
    return pendingOffer
  }

  if (isShowcase) {
    return showcaseOffer
  }

  return activeOffer
}

const OfferEducationalConfirmation = ({
  offererId,
  offerStatus,
  isShowcase,
}: IOfferEducationalConfirmationProps): JSX.Element => {
  const { title, description, Icon } = mapOfferStatusToData(
    offerStatus,
    isShowcase
  )

  return (
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
          to="/offres"
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
  )
}

export default OfferEducationalConfirmation
