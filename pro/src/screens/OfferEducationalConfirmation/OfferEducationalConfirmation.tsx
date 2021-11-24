import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as ValidateIcon } from 'components/pages/Offers/Offer/Confirmation/assets/validate.svg'
import { Title } from 'ui-kit'

import styles from './OfferEducationalConfirmation.module.scss'

interface IOfferEducationalConfirmationProps {
  offererId: string | null
  venueId: string | null
}

const OfferEducationalConfirmation = ({
  offererId,
  venueId,
}: IOfferEducationalConfirmationProps): JSX.Element => {
  let queryString = ''
  if (offererId) {
    queryString = `?structure=${offererId}`
  }

  if (venueId) {
    queryString += `&lieu=${venueId}`
  }

  return (
    <div className={styles['confirmation']}>
      <ValidateIcon className={styles['confirmation-icon']} />
      <div className={styles['confirmation-section']}>
        <div className={styles['confirmation-section-header']}>
          <Title as="h2" level={3}>
            Offre créée avec succès !
          </Title>
        </div>
        <p className={styles['form-layout-section-description']}>
          Votre offre est désormais disponible sur ADAGE (L'Application Dédiée À
          la Généralisation de l’Éducation artistique et culturelle) et visible
          par les professeurs et chefs d’établissement de l’Éducation Nationale.
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
          to={`/offre/creation${queryString}`}
        >
          Créer une nouvelle offre
        </Link>
      </div>
    </div>
  )
}

export default OfferEducationalConfirmation
