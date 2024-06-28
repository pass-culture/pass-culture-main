import React from 'react'

import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokePassIcon from 'icons/stroke-pass.svg'
import strokeRepaymentIcon from 'icons/stroke-repayment.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { StepComponentProps } from '../types'

import styles from './Step.module.scss'

export const Welcome = ({
  titleId,
  contentClassName,
}: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId} className={styles['title']}>
      Bienvenue dans l’espace acteurs culturels
    </h1>
    <section className={contentClassName}>
      <div className={styles['tw-description']}>
        Le pass Culture est un dispositif gouvernemental permettant aux jeunes
        âgés de 15 à 20 ans de bénéficier d’une enveloppe de 300€ utilisable
        pour réserver vos offres culturelles.
      </div>
      <div className={styles['tw-strong']}>
        Pour mettre en avant vos offres, rien de plus simple !
      </div>
      <div className={styles['tw-steps']}>
        <div>
          <div className={styles['tw-icon']}>
            <SvgIcon src={strokePassIcon} alt="" className={styles['icon']} />
          </div>
          <p>Paramétrez votre espace</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <SvgIcon src={strokeOffersIcon} alt="" />
          </div>
          <p>Créez et publiez vos offres</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <SvgIcon alt="" src={strokeCalendarIcon} />
          </div>
          <p>Gérez vos réservations</p>
        </div>
        <div>
          <div className={styles['tw-icon']}>
            <SvgIcon src={strokeRepaymentIcon} alt="" />
          </div>
          <p>Suivez vos remboursements</p>
        </div>
      </div>
    </section>
  </>
)
