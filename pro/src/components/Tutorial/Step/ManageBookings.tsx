import React from 'react'

import { CalendarIcon } from 'icons'
import { ReactComponent as IconEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import deskIcon from 'icons/stroke-desk.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { IStepComponentProps } from '../types'

import { ReactComponent as DownArrow } from './assets/down-arrow.svg'
import { ReactComponent as UpArrow } from './assets/up-arrow.svg'
import styles from './Step.module.scss'

const ManageBookings = ({ titleId }: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Suivez et gérez vos réservations</h1>
    <section className={styles['mb-content']}>
      <span className={styles['first-column']}>Validez vos contremarques</span>
      <span className={styles['third-column']}>
        Accédez à la liste de vos réservations
      </span>
      <DownArrow className={styles['first-column']} />
      <DownArrow className={styles['third-column']} />
      <span className={styles['header-example']}>
        <span className={styles['header-element']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={deskIcon}
            alt=""
          />
          Guichet
        </span>
        <span className={styles['header-element']}>
          <IconOffers className={styles['header-element-icon']} />
          Offres
        </span>
        <span className={styles['header-element']}>
          <CalendarIcon className={styles['header-element-icon']} />
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
        Créez, éditez, désactivez vos offres
      </span>
      <span className={styles['fourth-column']}>
        Téléchargez le détail de vos remboursements
      </span>
    </section>
  </>
)

export default ManageBookings
