import React from 'react'
import { useLocation } from 'react-router-dom'

import { CircleArrowIcon } from 'icons'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './SkipLinks.module.scss'

interface SkipLinksProps {
  displayMenu?: boolean
}

const SkipLinks = ({ displayMenu = false }: SkipLinksProps): JSX.Element => {
  const location = useLocation()

  return (
    <nav className={styles['skip-links']}>
      <ul className={styles['skip-list']}>
        <li>
          <ButtonLink
            link={{
              to: `${location.pathname}${location.search}#content`,
              isExternal: false,
            }}
            Icon={CircleArrowIcon}
            className={styles['skip-list-button']}
            variant={ButtonVariant.TERNARY}
          >
            Aller au contenu
          </ButtonLink>
        </li>
        {displayMenu && (
          <li>
            <a href="#header-navigation">Menu</a>
          </li>
        )}
      </ul>
    </nav>
  )
}

export default SkipLinks
