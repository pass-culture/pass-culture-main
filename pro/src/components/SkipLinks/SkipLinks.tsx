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
        // biome-ignore lint/correctness/useUniqueElementIds: This cannot be used more than once on the page.
        // biome-ignore lint/a11y/useAnchorContent: The unaccessible-top-page link is known to have a11y issues (hence, its name) and will be deleted in a near future.
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
