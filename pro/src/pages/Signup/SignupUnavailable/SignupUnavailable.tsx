import type { FunctionComponent } from 'react'

import strokeWipIcon from '@/icons/stroke-wip.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SignupUnavailable.module.scss'

export const SignupUnavailable: FunctionComponent = () => {
  return (
    <section className={styles['sign-up-unavailable-section']}>
      <div className={styles['content']}>
        <SvgIcon
          className={styles['sign-up-unavailable-section-icon']}
          alt=""
          src={strokeWipIcon}
          width="180"
        />
        <h2 className={styles['title']}>Inscription indisponible</h2>
        <div>
          Pour des raisons techniques, l’inscription sur le pass Culture est
          indisponible aujourd’hui.
        </div>
        <br />
        <div>Vous pourrez vous inscrire dès demain.</div>
      </div>
    </section>
  )
}
