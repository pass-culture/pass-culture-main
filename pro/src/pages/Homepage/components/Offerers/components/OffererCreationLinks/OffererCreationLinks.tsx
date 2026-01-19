import { Card } from '@/components/Card/Card'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import styles from './OffererCreationLinks.module.scss'

export const OffererCreationLinks = () => (
  <Card className={styles['card']} data-testid="offerers-creation-links-card">
    <h3 className={styles['title']}>Structures</h3>

    <div className={styles['content']}>
      <p>
        Votre précédente structure a été supprimée. Pour plus d’informations sur
        la suppression et vos données, veuillez contacter notre support.
      </p>

      <div className={styles['actions-container']}>
        <Button
          as="a"
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
  </Card>
)
