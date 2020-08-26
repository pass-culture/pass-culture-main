import React from 'react'
import Icon from '../../../layout/Icon'

const StyleguideButtons = () => {
  const primaryButton = (
    <div className="flex-block">
      <a
        className="primary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Bouton Primary'}
      </a>
      <div>
        {'classe'}
        <span className="class-name">
          {' .primary-button '}
        </span>
        {'(boutons) ou'}
        <span className="class-name">
          {' .primary-link '}
        </span>
        {'(liens)'}
      </div>
    </div>
  )

  const secondaryButton = (
    <div className="flex-block">
      <a
        className="secondary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Bouton Secondary'}
      </a>
      <div>
        {'classe'}
        <span className="class-name">
          {' .secondary-button '}
        </span>
        {'(boutons) ou'}
        <span className="class-name">
          {' .secondary-link '}
        </span>
        {'(liens)'}
      </div>
    </div>
  )

  const tertiaryButton = (
    <div className="flex-block">
      <a
        className="tertiary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        <span>
          {'Bouton Tertiary'}
        </span>
      </a>
      <div>
        {'classe'}
        <span className="class-name">
          {' .tertiary-link '}
        </span>
        {'(liens)'}
      </div>
    </div>
  )

  const quaternaryButton = (
    <div className="flex-block">
      <a
        className="quaternary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        <span>
          {'Bouton Quaternary'}
        </span>
      </a>
      <div>
        {'classe'}
        <span className="class-name">
          {' .quaternary-link '}
        </span>
        {'(liens)'}
      </div>
    </div>
  )

  return (
    <div>
      {primaryButton}
      <hr />
      {secondaryButton}
      <hr />
      {tertiaryButton}
      <hr />
      {quaternaryButton}
      <br />
    </div>
  )
}

export default StyleguideButtons
