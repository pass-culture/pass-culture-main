import React from 'react'

import { ReactComponent as Buble } from './assets/buble.svg'
import styles from './HelpLink.module.scss'

const HelpLink = (): JSX.Element => (
  <a
    className={styles['help-link']}
    href="https://aide.passculture.app/fr/articles/5645063-acteurs-culturels-comment-poster-une-offre-a-destination-d-un-groupe-scolaire"
    rel="noreferrer"
    target="_blank"
  >
    <Buble />
    <span className={styles['help-link-text']}>Aide</span>
  </a>
)

export default HelpLink
