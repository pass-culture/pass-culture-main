/** biome-ignore-all lint/correctness/useUniqueElementIds: Elements on this component are always rendered once per page, so there cannot be id duplications */
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './SkipLinks.module.scss'
import { useSkipLinksContext } from './SkipLinksContext'

export const SkipLinks = (): JSX.Element => {
  const { setMenuContainer, setFooterContainer } = useSkipLinksContext()

  return (
    <>
      {/* This will receive the focus when the page is loaded */}
      <div tabIndex={-1} id="top-page" data-testid="top-page" />

      {/* and this will be the immediate next element after that can be tabbed */}
      <nav aria-label="Accès rapide" className={styles['skip-links']}>
        <ul className={styles['skip-links-list']}>
          <li>
            <Button
              as="a"
              id="go-to-content"
              to="#content"
              isExternal
              icon={fullNextIcon}
              label="Aller au contenu"
              size={ButtonSize.SMALL}
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
            />
          </li>
          <li ref={setMenuContainer} />
          <li ref={setFooterContainer} />
        </ul>
      </nav>
    </>
  )
}
