import React from 'react'

import { ReactComponent as Buble } from './assets/buble.svg'
import styles from './HelpLink.module.scss'

const HelpLink = (): JSX.Element => (
  <a
    className={styles['help-link']}
    href="https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-"
    rel="noreferrer"
    target="_blank"
  >
    <Buble />
    <span className={styles['help-link-text']}>Aide</span>
  </a>
)

export default HelpLink
