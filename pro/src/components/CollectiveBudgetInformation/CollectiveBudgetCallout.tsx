import { storageAvailable } from 'commons/utils/storageAvailable'
import { useState } from 'react'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from './CollectiveBudgetInformation.module.scss'
import {
  COLLECTIVE_OFFER_CREATION_DESCRIPTION,
  COLLECTIVE_OFFER_CREATION_TITLE,
  COLLECTIVE_TABLES_DESCRIPTION,
  COLLECTIVE_TABLES_TITLE,
} from './constants'

export const CollectiveBudgetCallout = ({
  pageName,
  variant = 'COLLECTIVE_OFFER_CREATION',
}: {
  pageName: string
  variant?: 'COLLECTIVE_OFFER_CREATION' | 'COLLECTIVE_TABLE'
}): JSX.Element | null => {
  const [isCalloutOpen, setIsCalloutOpen] = useState(true)
  const LOCAL_STORAGE_HAS_SEEN_COLLECTIVE_BUDGET_CALLOUT_KEY = `collective-budget-callout-${pageName}`

  const isLocalStorageAvailable = storageAvailable('localStorage')

  const shouldShowCallout =
    isCalloutOpen &&
    (!isLocalStorageAvailable ||
      localStorage.getItem(
        LOCAL_STORAGE_HAS_SEEN_COLLECTIVE_BUDGET_CALLOUT_KEY
      ) !== 'true')

  const onCloseCallout = () => {
    localStorage.setItem(
      LOCAL_STORAGE_HAS_SEEN_COLLECTIVE_BUDGET_CALLOUT_KEY,
      'true'
    )
    setIsCalloutOpen(false)
  }

  return shouldShowCallout ? (
    <Callout
      className={styles['callout-warning-eac-budget']}
      variant={CalloutVariant.WARNING}
      closable
      onClose={onCloseCallout}
      title={
        variant === 'COLLECTIVE_TABLE'
          ? COLLECTIVE_TABLES_TITLE
          : COLLECTIVE_OFFER_CREATION_TITLE
      }
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/18234132822684--Acteurs-culturels-Informations-importantes-Cr%C3%A9dit-de-la-part-collective-pour-l-ann%C3%A9e-scolaire-2024-2025',
          label: 'En savoir plus',
          isExternal: true,
        },
      ]}
    >
      {variant === 'COLLECTIVE_TABLE'
        ? COLLECTIVE_TABLES_DESCRIPTION
        : COLLECTIVE_OFFER_CREATION_DESCRIPTION}
    </Callout>
  ) : null
}
