import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

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
          <Button
            as="a"
            variant={ButtonVariant.PRIMARY}
            to="/inscription/structure/recherche"
            label="Ajouter une nouvelle structure"
          />
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            isExternal
            opensInNewTab
            to="https://aide.passculture.app/hc/fr/requests"
            label="Contacter le support"
          />
        </div>
      </div>
    </div>
  )
}
