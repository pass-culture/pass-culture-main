import React, { FunctionComponent } from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SignupUnavailable.module.scss'

export const SignupUnavailable: FunctionComponent = () => {
  return (
    <section className={styles['sign-up-unavailable-section']}>
      <div className={styles['content']}>
        <SvgIcon
          className={styles['sign-up-unavailable-section-icon']}
          alt=""
          src={strokeWipIcon}
          viewBox="0 0 200 156"
          width="180"
        />
        <h1 className={styles['heading-1']}>Inscription indisponible</h1>
        <h2>
          Pour des raisons techniques, l’inscription sur le pass Culture est
          indisponible aujourd’hui.
        </h2>
        <br />
        <h2>Vous pourrez vous inscrire dès demain.</h2>
      </div>
    </section>
  )
}
