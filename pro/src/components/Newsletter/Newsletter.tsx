import React from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import newsletterImage from './assets/newsletter.svg'
import styles from './Newsletter.module.scss'

export const Newsletter = () => {
  return (
    <div className={styles['newsletter-container']}>
      <ButtonLink
        className={styles['newsletter-link']}
        variant={ButtonVariant.TERNARY}
        to="https://0d5544dc.sibforms.com/serve/MUIEALeDGWdeK5Sx3mk95POo84LXw0wfRuL7M0YSLmEBQczDtyf9RchpzXzPpraWplBsNGz3nhwEpSpqOVUz_OeUCphS-ds635cE-vXDtQwLDc76VZ4GgUuqnsONKJ1FX6oBCslhYqgA6kB2vcv4_tNTLKesJvidy2o24roIqFRdfawXEOgz8LBQ1C9dlrDpO_Dz6E5L0IO_Gzs1"
        isExternal
        opensInNewTab
        icon={fullLinkIcon}
      >
        Inscrivez-vous à notre newsletter pour recevoir les actualités du pass
        Culture
        <img
          src={newsletterImage}
          alt=""
          className={styles['newsletter-img']}
        />
      </ButtonLink>
    </div>
  )
}
