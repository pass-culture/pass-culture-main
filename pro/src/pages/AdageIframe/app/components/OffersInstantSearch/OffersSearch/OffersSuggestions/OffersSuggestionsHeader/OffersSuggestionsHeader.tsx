import type { ReactNode } from 'react'

import styles from './OffersSuggestionsHeader.module.scss'

export const OffersSuggestionsHeader = ({
  children,
}: {
  children: ReactNode
}) => {
  return (
    <div className={styles['offers-suggestions-header']}>
      <div
        className={styles['offers-suggestions-header-text']}
        data-testid="suggestions-header"
      >
        {children}
      </div>
    </div>
  )
}
