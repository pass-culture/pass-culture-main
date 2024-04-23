import React from 'react'

import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './SkipLinks.module.scss'

interface SkipLinksProps {
  displayMenu?: boolean
}

const SkipLinks = ({ displayMenu = false }: SkipLinksProps): JSX.Element => {
  const buttons: { anchor: string; label: string }[] = [
    { anchor: '#content', label: 'Aller au contenu' },
  ].concat(displayMenu ? { anchor: '#header-navigation', label: 'Menu' } : [])

  return (
    <>
      <a tabIndex={-1} href="#" id="top-page" className="visually-hidden" />
      <nav aria-label="Accès rapide" className={styles['skip-links']}>
        <div id="orejime"></div>
        {buttons.length > 1 ? (
          <ul className={styles['skip-list']}>
            {buttons.map((button) => {
              return (
                <li key={button.anchor}>
                  <ButtonLink
                    link={{
                      to: button.anchor,
                      isExternal: true,
                    }}
                    icon={fullNextIcon}
                    className={styles['skip-list-button']}
                    variant={ButtonVariant.QUATERNARY}
                  >
                    {button.label}
                  </ButtonLink>
                </li>
              )
            })}
          </ul>
        ) : (
          <div className={styles['skip-list']}>
            <ButtonLink
              link={{
                to: '#content',
                isExternal: true,
              }}
              icon={fullNextIcon}
              className={styles['skip-list-button']}
              variant={ButtonVariant.QUATERNARY}
            >
              Aller au contenu
            </ButtonLink>
          </div>
        )}
      </nav>
    </>
  )
}

export default SkipLinks
