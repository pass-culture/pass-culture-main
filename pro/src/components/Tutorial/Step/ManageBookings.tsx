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

export const ManageBookings = ({
  titleId,
}: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId} className={styles['title']}>
      Suivez et gérez vos réservations
    </h1>
    <section className={styles['mb-content']}>
      <div className={styles['nav-tutorial']}>
        <div className={styles['ticket-office']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeDeskIcon}
            alt=""
          />
          Guichet
        </div>
        <div className={styles['offers']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeOffersIcon}
            alt=""
          />
          Offres
        </div>
        <div className={styles['booking']}>
          <SvgIcon
            alt=""
            src={strokeCalendarIcon}
            className={styles['header-element-icon']}
          />
          Réservations
        </div>
        <div className={styles['reimbursements']}>
          <SvgIcon
            className={styles['header-element-icon']}
            src={strokeEuroIcon}
            alt=""
          />
          Gestion financière
        </div>
      </div>
      <div className={styles['ticket-office-informations']}>
        Validez vos contremarques
        <div>
          <SvgIcon
            src={fullDownIcon}
            alt=""
            width="24"
            className={styles['arrow-icon']}
          />
        </div>
      </div>
      <div className={styles['booking-informations']}>
        Accédez à la liste de vos réservations
        <div>
          <SvgIcon
            src={fullDownIcon}
            alt=""
            width="24"
            className={styles['arrow-icon']}
          />
        </div>
      </div>
      <div className={styles['offers-informations']}>
        <div>
          <SvgIcon
            src={fullUpIcon}
            alt=""
            width="24"
            className={styles['arrow-icon']}
          />
        </div>
        Créez, éditez, désactivez vos offres
      </div>
      <div className={styles['reimbursements-informations']}>
        <div>
          <SvgIcon
            src={fullUpIcon}
            alt=""
            width="24"
            className={styles['arrow-icon']}
          />
        </div>
        Téléchargez le détail de vos remboursements
      </div>
    </section>
  </>
)
