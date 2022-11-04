import React from 'react'

import { IStepComponentProps } from '../types'

import styles from './Step.module.scss'

const Welcome = ({
  titleId,
  contentClassName,
}: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Bienvenue dans l’espace acteurs culturels</h1>
    <section className={contentClassName}>
      <div className={styles['tw-description']}>
        Le pass Culture est une politique culturelle publique permettant aux
        jeunes âgés de 18 ans de bénéficier d’une enveloppe de 300€ utilisable
        pour réserver vos offres.
      </div>
      <div className={styles['tw-strong']}>
        Pour mettre en avant vos offres, rien de plus simple !
      </div>
      <div className={styles['tw-steps']}>
        <div>
          <p className={styles['tw-numbers']}>1</p>
          <p>Créez un lieu culturel</p>
        </div>
        <div>
          <p className={styles['tw-numbers']}>2</p>
          <p>Créez et publiez vos offres</p>
        </div>
        <div>
          <p className={styles['tw-numbers']}>3</p>
          <p>Suivez et gérez vos réservations</p>
        </div>
        <div>
          <p className={styles['tw-numbers']}>4</p>
          <p>
            Renseignez vos coordonnées bancaires pour percevoir les
            remboursements de vos offres éligibles
          </p>
        </div>
      </div>
    </section>
  </>
)

export default Welcome
