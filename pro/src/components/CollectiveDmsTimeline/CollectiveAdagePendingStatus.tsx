import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullInfoIcon from '@/icons/full-info.svg'

import styles from './CollectiveAdagePendingStatus.module.scss'

export const CollectiveAdagePendingStatus = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>
          État de votre activité dans ADAGE :
        </span>
        <Tag label="Référencement en cours" variant={TagVariant.WARNING} />
      </div>

      <div className={styles['link-container']}>
        <div className={styles['link-button-wrapper']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullInfoIcon}
            to="https://aide.passculture.app/hc/fr/categories/4410482280977--Acteurs-Culturels-Tout-savoir-sur-le-pass-Culture-collectif-%C3%A0-destination-des-groupes-scolaires"
            isExternal
            opensInNewTab
            label="En savoir plus sur le pass Culture à destination des scolaires"
          />
        </div>
      </div>

      <p className={styles.description}>
        Votre démarche de référencement est en cours de traitement par ADAGE.
      </p>
    </div>
  )
}
