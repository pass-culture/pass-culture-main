import React, { FunctionComponent, useCallback, useEffect, useRef } from 'react'

import { ReactComponent as ArrowDown } from 'components/pages/Offers/Offer/Thumbnail/assets/arrow-down.svg'
import { ReactComponent as ArrowUp } from 'components/pages/Offers/Offer/Thumbnail/assets/arrow-up.svg'
import { ReactComponent as ExternalSite } from 'components/pages/Offers/Offer/Thumbnail/assets/external-site.svg'
import { NBSP } from 'core/shared'

interface Props {
  hidden: boolean
  setHidden: (hidden: boolean) => void
  teaserText: string
  children?: never
}

const Advices: FunctionComponent<Props> = ({
  teaserText,
  hidden,
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
    <div className="tna-advices">
      <button
        aria-pressed={!hidden}
        className={`tna-toggle ${hidden ? 'up' : 'down'} tertiary-link`}
        onClick={toggle}
        ref={defaultTargetedButton}
        type="button"
      >
        Conseils pour votre image
        {hidden ? <ArrowDown /> : <ArrowUp />}
      </button>
      <div aria-hidden={hidden} className={hidden ? 'tna-hidden' : ''}>
        <p className="tna-teaser">{teaserText}</p>
        <p className="tna-title">Banques d’images libres de droits</p>
        <ul className="tna-links">
          <li>
            <a
              className="tertiary-link"
              href="https://www.pexels.com/fr-fr/"
              rel="noopener noreferrer"
              target="_blank"
            >
              <ExternalSite />
              Pexels
              <span className="tna-links-help">{`${NBSP}(nouvel onglet)`}</span>
            </a>
          </li>
          <li>
            <a
              className="tertiary-link"
              href="https://pixabay.com/fr/"
              rel="noopener noreferrer"
              target="_blank"
            >
              <ExternalSite />
              Pixabay
              <span className="tna-links-help">{`${NBSP}(nouvel onglet)`}</span>
            </a>
          </li>
          <li>
            <a
              className="tertiary-link"
              href="https://www.shutterstock.com/"
              rel="noopener noreferrer"
              target="_blank"
            >
              <ExternalSite />
              Shutterstock
              <span className="tna-links-help">{`${NBSP}(nouvel onglet)`}</span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default Advices
