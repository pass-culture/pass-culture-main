import React, { FunctionComponent } from 'react'

import { ReactComponent as UnavailableIcon } from 'icons/ico-unavailable-gradient.svg'

import styles from './SignupUnavailable.module.scss'

const SignupUnavailable: FunctionComponent = () => {
  return (
    <section>
      <section className={styles['sign-up-unavailable-section']}>
        <div className={styles['content']}>
          <UnavailableIcon />
          <h1 className={styles['heading-1']}>Inscription indisponible</h1>
          <h2>
            Pour des raisons techniques, l’inscription sur le pass Culture est
            indisponible aujourd’hui.
          </h2>
          <br />
          <h2>Vous pourrez vous inscrire dès demain.</h2>
        </div>
      </section>
    </section>
  )
}

export default SignupUnavailable
