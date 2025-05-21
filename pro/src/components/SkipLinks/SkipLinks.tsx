import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './SkipLinks.module.scss'

interface SkipLinksProps {
  shouldDisplayTopPageLink?: boolean
}

export const SkipLinks = ({
  shouldDisplayTopPageLink = true,
}: SkipLinksProps): JSX.Element => {
  return (
    <>
      {shouldDisplayTopPageLink && (
        <a
          tabIndex={-1}
          href="#"
          id="unaccessible-top-page"
          className={styles['visually-hidden']}
        />
      )}
      <div id="orejimeElement" />
      <nav aria-label="Accès rapide" className={styles['skip-links']}>
        <div className={styles['skip-list']}>
          <ButtonLink
            to="#content"
            isExternal
            icon={fullNextIcon}
            className={styles['skip-list-button']}
            variant={ButtonVariant.QUATERNARY}
            id="got-to-main-content"
          >
            Aller au contenu
          </ButtonLink>
        </div>
      </nav>
    </>
  )
}
