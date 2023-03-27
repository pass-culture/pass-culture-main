import React from 'react'

import styles from './SkipLinks.module.scss'

interface SkipLinksProps {
  displayMenu?: boolean
}

const SkipLinks = ({ displayMenu = true }: SkipLinksProps): JSX.Element => {
  return (
    <nav className={styles['skip-links']}>
      <ul className={styles['skip-list']}>
        <li>
          <a href="#content">Contenu</a>
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
