import React from 'react'

import Icon from 'components/layout/Icon'
import { CGU_URL } from 'utils/config'

import styles from './PriceErrorHTMLNotification.module.scss'

const PriceErrorHTMLNotification = () => {
  return (
    <p className={styles['price300-error-message']}>
      {
        'Le prix d’une offre ne peut excéder 300 euros. Pour plus d’infos, merci de consulter nos '
      }
      <a href={CGU_URL} rel="noreferrer" target="_blank">
        <Icon alt="lien externe, nouvel onglet" svg="ico-external-site" />
        Conditions Générales d’Utilisation
      </a>
    </p>
  )
}

export default PriceErrorHTMLNotification
