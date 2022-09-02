import React from 'react'

import { ReactComponent as LinkIcon } from 'icons/ico-external-site-filled.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ReactComponent as NewsletterImg } from './assets/newsletter.svg'
import styles from './Newsletter.module.scss'

const Newsletter = () => {
  return (
    <div className={styles['newsletterContainer']}>
      <NewsletterImg className={styles['newsletterImg']} />
      <div className={styles['newsletterLink']}>
        <ButtonLink
          variant={ButtonVariant.TERNARY}
          link={{
            to: 'https://0d5544dc.sibforms.com/serve/MUIEALeDGWdeK5Sx3mk95POo84LXw0wfRuL7M0YSLmEBQczDtyf9RchpzXzPpraWplBsNGz3nhwEpSpqOVUz_OeUCphS-ds635cE-vXDtQwLDc76VZ4GgUuqnsONKJ1FX6oBCslhYqgA6kB2vcv4_tNTLKesJvidy2o24roIqFRdfawXEOgz8LBQ1C9dlrDpO_Dz6E5L0IO_Gzs1',
            isExternal: false,
            target: '_blank',
          }}
          Icon={LinkIcon}
        >
          Inscrivez-vous à notre newsletter pour recevoir les actualités du pass
          Culture
        </ButtonLink>
      </div>
    </div>
  )
}

export default Newsletter
