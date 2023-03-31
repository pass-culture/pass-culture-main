import React from 'react'

import { CaseIcon, InfoPhoneIcon } from 'icons'

import { IStepComponentProps } from '../types'

import styles from './Step.module.scss'

const CreateOffer = ({
  titleId,
  contentClassName,
}: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Créez et publiez vos offres à destination :</h1>
    <section className={contentClassName}>
      <div className={styles['two-columns-section-block']}>
        <InfoPhoneIcon />
        <h2>Du grand public</h2>
        <p>
          Les offres seront publiées et réservables par les jeunes via
          l'application pass Culture.
          <br />
          <br />
          Vous pourrez proposer des offres numériques, physiques et
          d’évènements.
        </p>
      </div>
      <div className={styles['two-columns-section-block']}>
        <CaseIcon />
        <h2>Des établissements scolaires</h2>
        <p>
          Les offres seront publiées et réservables par les enseignants sur la
          plateforme ADAGE (Application Dédiée À la Généralisation de
          l’Éducation artistique et culturelle).
          <br />
          <br />
          Vous devez être référencé sur ADAGE afin de proposer des offres à
          destination des enseignants.
        </p>
      </div>
    </section>
  </>
)

export default CreateOffer
