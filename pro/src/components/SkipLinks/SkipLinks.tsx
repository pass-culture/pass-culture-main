import { Button } from '@/design-system/Button/Button'
import { ButtonSize } from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './SkipLinks.module.scss'

export const SkipLinks = (): JSX.Element => {
  return (
    <nav aria-label="Accès rapide" className={styles['skip-links']}>
      {/** biome-ignore lint/correctness/useUniqueElementIds: This is always
          rendered once per page, so there cannot be id duplications.> */}
      <Button
        as="a"
        id="go-to-content"
        to="#content"
        isExternal
        icon={fullNextIcon}
        label="Aller au contenu"
        size={ButtonSize.SMALL}
      />
    </nav>
  )
}
