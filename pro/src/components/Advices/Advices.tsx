import React, { FunctionComponent, useCallback, useEffect, useRef } from 'react'

import { NBSP } from 'core/shared'
import ArrowDown from 'icons/arrow-down.svg'
import ArrowUp from 'icons/arrow-up.svg'
import ExternalSite from 'icons/external-site.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './Advices.module.scss'

interface Props {
  hidden: boolean
  setHidden: (hidden: boolean) => void
  teaserText: string
  children?: never
}

const Advices: FunctionComponent<Props> = ({
  teaserText,
  hidden = true,
  setHidden,
}) => {
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
        Icon={hidden ? ArrowDown : ArrowUp}
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
                Icon={ExternalSite}
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
                Icon={ExternalSite}
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
                Icon={ExternalSite}
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
