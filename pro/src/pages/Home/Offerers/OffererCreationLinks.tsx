import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Card } from '../Card'

import styles from './OffererCreationLinks.module.scss'

const OffererCreationLinks = () => (
  <Card className={styles['card']} data-testid="offerers-creation-links-card">
    <h3 className={styles['title']}>Structures</h3>

    <div className={styles['content']}>
      <p>
        Votre précédente structure a été supprimée. Pour plus d’informations sur
        la suppression et vos données, veuillez contacter notre support.
      </p>

      <div className={styles['actions-container']}>
        <ButtonLink
          variant={ButtonVariant.PRIMARY}
          link={{ isExternal: false, to: '/structures/creation' }}
        >
          Ajouter une nouvelle structure
        </ButtonLink>

        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            isExternal: true,
            to: 'mailto:support-pro@passculture.app',
          }}
        >
          Contacter le support
        </ButtonLink>
      </div>
    </div>
  </Card>
)

export default OffererCreationLinks
