import React from 'react'

import {
  CalendarIcon,
  OfferCardEuroIcon,
  OtherOfferIcon,
  PasscultureIcon,
} from 'icons'

import { StepComponentProps } from '../types'

import styles from './Step.module.scss'

const Welcome = ({
  titleId,
  contentClassName,
}: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Bienvenue dans l’espace acteurs culturels</h1>
    <section className={contentClassName}>
      <div className={styles['tw-description']}>
        Le pass Culture est un dispositif gouvernemental permettant aux jeunes
        âgés de 15 à 20 ans de bénéficier d'une enveloppe de 300€ utilisable
        pour réserver vos offres culturelles.
      </div>
      <div className={styles['tw-strong']}>
        Pour mettre en avant vos offres, rien de plus simple !
      </div>
      <div className={styles['tw-steps']}>
        <div>
          <div className={styles['tw-icon']}>
            <PasscultureIcon />
          </div>
          <p>Paramétrez votre espace</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <OtherOfferIcon />
          </div>
          <p>Créez et publiez vos offres</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <CalendarIcon />
          </div>
          <p>Gérez vos réservations</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <OfferCardEuroIcon />
          </div>
          <p>Suivez vos remboursements</p>
        </div>
      </div>
    </section>
  </>
)

export default Welcome
