import React, { useCallback, useEffect, useRef } from 'react'

import { NBSP } from 'core/shared'
import fullDownIcon from 'icons/full-down.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullUpIcon from 'icons/full-up.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './Advices.module.scss'

interface AdvicesProps {
  hidden: boolean
  setHidden: (hidden: boolean) => void
  teaserText: string
}

const Advices = ({ teaserText, hidden = true, setHidden }: AdvicesProps) => {
  const toggle = useCallback(() => {
    setHidden(!hidden)
  }, [hidden, setHidden])

  const defaultTargetedButton = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    defaultTargetedButton.current?.focus()
  }, [])

  return (
    <div className={styles['advices']}>
      <Button
        aria-pressed={!hidden}
        variant={ButtonVariant.TERNARY}
        onClick={toggle}
        type="button"
        icon={hidden ? fullDownIcon : fullUpIcon}
        iconPosition={IconPositionEnum.RIGHT}
      >
        Conseils pour votre image
      </Button>

      {hidden && (
        <div aria-hidden={hidden}>
          <p>{teaserText}</p>
          <p className={styles['advices-title']}>
            Banques d’images libres de droits
          </p>
          <ul>
            <li>
              <ButtonLink
                link={{
                  to: 'https://www.pexels.com/fr-fr/',
                  isExternal: true,
                  rel: 'noopener noreferrer',
                  target: '_blank',
                }}
                icon={fullLinkIcon}
              >
                Pexels
                <span>{`${NBSP}(nouvel onglet)`}</span>
              </ButtonLink>
            </li>
            <li>
              <ButtonLink
                link={{
                  to: 'https://pixabay.com/fr/',
                  isExternal: true,
                  rel: 'noopener noreferrer',
                  target: '_blank',
                }}
                icon={fullLinkIcon}
              >
                Pixabay
                <span>{`${NBSP}(nouvel onglet)`}</span>
              </ButtonLink>
            </li>
            <li>
              <ButtonLink
                link={{
                  to: 'https://www.shutterstock.com/',
                  isExternal: true,
                  rel: 'noopener noreferrer',
                  target: '_blank',
                }}
                icon={fullLinkIcon}
              >
                Shutterstock
                <span>{`${NBSP}(nouvel onglet)`}</span>
              </ButtonLink>
            </li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default Advices
