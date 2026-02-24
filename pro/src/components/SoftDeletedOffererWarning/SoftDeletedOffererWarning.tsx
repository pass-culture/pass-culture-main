import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Panel } from '@/ui-kit/Panel/Panel'

import styles from './SoftDeletedOffererWarning.module.scss'

export const SoftDeletedOffererWarning = (): JSX.Element => {
  return (
    <Panel>
      <div>
        <p className={styles['soft-deleted-offerer-warning']}>
          Votre structure a été désactivée. Pour plus d’informations sur la
          désactivation veuillez contacter notre support.
        </p>

        <div className={styles['soft-deleted-offerer-warning-actions']}>
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
    </Panel>
  )
}
