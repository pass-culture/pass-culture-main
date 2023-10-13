import { ReactNode } from 'react'

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

      {/* TODO : Uncomment this button when the link is available */}
      {/* <ButtonLink
        variant={ButtonVariant.TERNARYPINK}
        className={styles['offers-suggestions-header-link']}
        link={{
          to: '#', // TODO:  Lien FAQ à ajouter quand il sera disponible
          isExternal: true,
        }}
        icon={fullLinkIcon}
      >
        Comment fonctionnent les suggestions que je vois ci-dessous ?
      </ButtonLink> */}
    </div>
  )
}
