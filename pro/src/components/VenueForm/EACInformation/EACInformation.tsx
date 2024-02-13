import React from 'react'

import { Banner } from 'ui-kit/index'

import styles from './eacInformation.module.scss'

export const EACInformation = () => {
  return (
    <>
      <p className={styles['eac-description-info']}>
        Il s’agit d’un formulaire vous permettant de renseigner vos informations
        EAC. Les informations renseignées seront visibles par les enseignants et
        chefs d’établissement sur Adage (Application dédiée à la
        généralisation....)
      </p>

      <Banner type="notification-info">
        Une fois votre lieu créé, vous pourrez renseigner des informations pour
        les enseignants en revenant sur cette page.
      </Banner>
    </>
  )
}
