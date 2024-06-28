import React from 'react'

import phoneStrokeIcon from 'icons/stroke-phone.svg'
import strokeProfIcon from 'icons/stroke-prof.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { StepComponentProps } from '../types'

import styles from './Step.module.scss'

export const CreateOffer = ({
  titleId,
  contentClassName,
}: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId} className={styles['title']}>
      Créez et publiez vos offres à destination :
    </h1>
    <section className={contentClassName}>
      <div className={styles['two-columns-section-block']}>
        <SvgIcon src={phoneStrokeIcon} alt="" />
        <h2>Du grand public</h2>
        <p>
          Les offres seront publiées et réservables par les jeunes via
          l’application pass Culture.
          <br />
          <br />
          Vous pourrez proposer des offres numériques, physiques et
          d’évènements.
        </p>
      </div>
      <div className={styles['two-columns-section-block']}>
        <SvgIcon src={strokeProfIcon} alt="" />
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
