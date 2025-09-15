import fullNextIcon from '@/icons/full-next.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './SkipLinks.module.scss'

export const SkipLinks = (): JSX.Element => {
  return (
    <nav aria-label="Accès rapide" className={styles['skip-links']}>
      <div className={styles['skip-list']}>
        {/** biome-ignore lint/correctness/useUniqueElementIds: This is always
          rendered once per page, so there cannot be id duplications.> */}
        <ButtonLink
          id="go-to-content"
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
  )
}
