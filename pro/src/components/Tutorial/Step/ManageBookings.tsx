import React from 'react'

import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeDeskIcon from 'icons/stroke-desk.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { StepComponentProps } from '../types'

import styles from './Step.module.scss'

const ManageBookings = ({ titleId }: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Suivez et gérez vos réservations</h1>
    <section className={styles['mb-content']}>
      <span className={styles['first-column']}>Validez vos contremarques</span>
      <span className={styles['third-column']}>
        Accédez à la liste de vos réservations
      </span>
      <SvgIcon
        src={fullDownIcon}
        alt=""
        width="24"
        className={styles['first-column']}
      />
      <SvgIcon
        src={fullDownIcon}
        alt=""
        width="24"
        className={styles['third-column']}
      />
      <span className={styles['header-example']}>
        <span className={styles['header-element']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeDeskIcon}
            alt=""
          />
          Guichet
        </span>
        <span className={styles['header-element']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeOffersIcon}
            alt=""
          />
          Offres
        </span>
        <span className={styles['header-element']}>
          <SvgIcon
            alt=""
            src={strokeCalendarIcon}
            className={styles['header-element-icon']}
          />
          Réservations
        </span>
        <span className={styles['header-element']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeEuroIcon}
            alt=""
          />
          Remboursements
        </span>
      </span>
      <SvgIcon
        src={fullUpIcon}
        alt=""
        width="24"
        className={styles['second-column']}
      />
      <SvgIcon
        src={fullUpIcon}
        alt=""
        width="24"
        className={styles['fourth-column']}
      />
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
