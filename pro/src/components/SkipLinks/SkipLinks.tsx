import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './SkipLinks.module.scss'

interface SkipLinksProps {
  shouldDisplayTopPageLink?: boolean
}

export const SkipLinks = ({ shouldDisplayTopPageLink = true }: SkipLinksProps): JSX.Element => {
  const buttons: { anchor: string; label: string }[] = [
    { anchor: '#content', label: 'Aller au contenu' },
  ]

  return (
    <>
      {shouldDisplayTopPageLink && <a
        tabIndex={-1}
        href="#"
        id="unaccessible-top-page"
        className={styles['visually-hidden']}
      />}
      <nav aria-label="Accès rapide" className={styles['skip-links']}>
        <div id="orejime" />
        {buttons.length > 1 ? (
          <ul className={styles['skip-list']}>
            {buttons.map((button) => {
              return (
                <li key={button.anchor}>
                  <ButtonLink
                    to={button.anchor}
                    isExternal
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
              to="#content"
              isExternal
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
