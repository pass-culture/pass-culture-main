import fullNextIcon from '@/icons/full-next.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

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
        // biome-ignore lint/a11y/useAnchorContent: TODO (igabriele, 2025-08-08): There may be accessibility-friendlier ways to do this.
        <a
          tabIndex={-1}
          // biome-ignore lint/a11y/useValidAnchor: See above comment.
          href="#"
          id="unaccessible-top-page"
          className={styles['visually-hidden']}
        />
      )}
      <nav aria-label="Accès rapide" className={styles['skip-links']}>
        <div className={styles['skip-list']}>
          <ButtonLink
            to="#content"
            isExternal
            icon={fullNextIcon}
            className={styles['skip-list-button']}
            variant={ButtonVariant.QUATERNARY}
          >
            Aller au contenu
          </ButtonLink>
        </div>
      </nav>
    </>
  )
}
