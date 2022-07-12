import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import React from 'react'
import styles from './EACInformation.module.scss'

const EACInformation = ({
  venueId,
  offererId,
}: {
  venueId: string
  offererId: string
}): JSX.Element => {
  return (
    <div className="section">
      <h2 className="main-list-title">Mes informations pour les enseignants</h2>
      <p className={styles['description']}>
        Il s'agit d'un formulaire vous permettant de renseigner vos informations
        à destination du public scolaire. Les informations renseignées seront
        visibles par les enseignants et chefs d'établissement sur Adage
        (Application dédiée à la généralisation de l'éducation artistique et
        culturelle).
      </p>
      <ButtonLink
        to={`/structures/${offererId}/lieux/${venueId}/eac`}
        variant={ButtonVariant.SECONDARY}
      >
        Renseigner mes informations
      </ButtonLink>
    </div>
  )
}

export default EACInformation
