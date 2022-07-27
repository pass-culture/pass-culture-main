import React from 'react'

import Icon from 'components/layout/Icon'

import { ReactComponent as NewsletterImg } from './assets/newsletter.svg'
import styles from './Newsletter.module.scss'

const Newsletter = () => {
  return (
    <div className={styles['newsletterContainer']}>
      <NewsletterImg className={styles['newsletterImg']} />
      <div className={styles['newsletterLink']}>
        <a
          className="hs-link tertiary-link"
          target={'_blank'}
          href={
            'https://0d5544dc.sibforms.com/serve/MUIEALeDGWdeK5Sx3mk95POo84LXw0wfRuL7M0YSLmEBQczDtyf9RchpzXzPpraWplBsNGz3nhwEpSpqOVUz_OeUCphS-ds635cE-vXDtQwLDc76VZ4GgUuqnsONKJ1FX6oBCslhYqgA6kB2vcv4_tNTLKesJvidy2o24roIqFRdfawXEOgz8LBQ1C9dlrDpO_Dz6E5L0IO_Gzs1'
          }
        >
          <Icon
            svg="ico-external-site-filled"
            className={styles['iconNewsletter']}
          />
          Inscrivez-vous à notre newsletter pour recevoir les actualités du pass
          Culture
        </a>
      </div>
    </div>
  )
}

export default Newsletter
