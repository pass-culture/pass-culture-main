import React from 'react'

import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './SoftDeletedOffererWarning.module.scss'

export const SoftDeletedOffererWarning = (): JSX.Element => {
  return (
    <div className={styles['soft-deleted-offerer-warning']}>
      <div className={styles['soft-deleted-offerer-warning-inner']}>
        <p>
          Votre structure a été désactivée. Pour plus d’informations sur la
          désactivation veuillez contacter notre support.
        </p>

        <div className="actions-container">
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to="/parcours-inscription/structure"
          >
            Ajouter une nouvelle structure
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            isExternal
            to="mailto:support-pro@passculture.app"
          >
            Contacter le support
          </ButtonLink>
        </div>
      </div>
    </div>
  )
}
