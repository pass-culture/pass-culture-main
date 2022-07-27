import React from 'react'
import { Link } from 'react-router-dom'

import styles from './SoftDeletedOffererWarning.module.scss'

const SoftDeletedOffererWarning = (): JSX.Element => {
  return (
    <div className={styles['soft-deleted-offerer-warning']}>
      <div className={styles['soft-deleted-offerer-warning-inner']}>
        <p>
          Votre structure a été désactivée. Pour plus d’informations sur la
          désactivation veuillez contacter notre support.
        </p>

        <div className="actions-container">
          <Link className="primary-link" to="/structures/creation">
            Ajouter une nouvelle structure
          </Link>
          <a
            className="secondary-link"
            href="mailto:support-pro@passculture.app"
          >
            Contacter le support
          </a>
        </div>
      </div>
    </div>
  )
}

export default SoftDeletedOffererWarning
