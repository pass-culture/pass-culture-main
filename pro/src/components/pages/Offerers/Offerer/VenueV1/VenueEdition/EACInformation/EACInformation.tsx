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
      <h2 className="main-list-title">Mes informations EAC</h2>
      <p className={styles['description']}>
        Il s'agit d'un formulaire vous permettant de renseigner vos informations
        EAC. Les informations renseignées seront visibles par les enseignants et
        chefs d'établissement sur Adage (Application dédiée à la
        généralisation....)
      </p>
      <ButtonLink
        to={`/structures/${offererId}/lieux/${venueId}/eac`}
        variant={ButtonVariant.SECONDARY}
      >
        Renseigner mes informations EAC
      </ButtonLink>
    </div>
  )
}

export default EACInformation
