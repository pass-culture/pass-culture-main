import React from 'react'

import { ReactComponent as IconCalendar } from 'icons/ico-calendar.svg'
import { ReactComponent as IconDesk } from 'icons/ico-desk.svg'
import { ReactComponent as IconEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'

import { IStepComponentProps } from '../types'

import { ReactComponent as DownArrow } from './assets/down-arrow.svg'
import { ReactComponent as UpArrow } from './assets/up-arrow.svg'
import styles from './Step.module.scss'

const ManageBookings = ({ titleId }: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Suivre et gérer vos réservations</h1>
    <section className={styles['mb-content']}>
      <span className={styles['first-column']}>Validez vos contremarques</span>
      <span className={styles['third-column']}>
        Accédez à la liste de vos réservations et les adresses mails des
        utilisateurs
      </span>
      <DownArrow className={styles['first-column']} />
      <DownArrow className={styles['third-column']} />
      <span className={styles['header-example']}>
        <span className={styles['header-element']}>
          <IconDesk className={styles['header-element-icon']} />
          Guichet
        </span>
        <span className={styles['header-element']}>
          <IconOffers className={styles['header-element-icon']} />
          Offres
        </span>
        <span className={styles['header-element']}>
          <IconCalendar className={styles['header-element-icon']} />
          Réservations
        </span>
        <span className={styles['header-element']}>
          <IconEuro className={styles['header-element-icon']} />
          Remboursements
        </span>
      </span>
      <UpArrow className={styles['second-column']} />
      <UpArrow className={styles['fourth-column']} />
      <span className={styles['second-column']}>
        Créez, éditez, désactivez et gérez vos offres
      </span>
      <span className={styles['fourth-column']}>
        Téléchargez les remboursements du pass Culture
      </span>
    </section>
  </>
)

export default ManageBookings
