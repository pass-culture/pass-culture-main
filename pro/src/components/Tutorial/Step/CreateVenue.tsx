import React from 'react'

import { Venue2Icon } from 'icons'
import strokeRepaymentIcon from 'icons/stroke-repayment.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { StepComponentProps } from '../types'

import styles from './Step.module.scss'

const CreateVenue = ({
  titleId,
  contentClassName,
}: StepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Paramétrez votre espace PRO</h1>
    <section className={contentClassName}>
      <div className={styles['two-columns-section-block']}>
        <SvgIcon src={strokeRepaymentIcon} alt="" />
        <h2>Renseignez vos coordonnées bancaires</h2>
        <p>
          Ajoutez vos informations bancaires pour percevoir les remboursements
          de vos offres. <br />
          Tous les remboursements sont rétroactifs.
        </p>
      </div>
      <div className={styles['two-columns-section-block']}>
        <Venue2Icon />
        <h2>Ajoutez des lieux</h2>
        <p>
          Vous ne disposez pas d'un lieu physique ?
          <br />
          Ajoutez des lieux et publiez vos offres. Ces offres seront
          géolocalisées à l'adresse du lieu rattaché.
        </p>
      </div>
    </section>
  </>
)

export default CreateVenue
