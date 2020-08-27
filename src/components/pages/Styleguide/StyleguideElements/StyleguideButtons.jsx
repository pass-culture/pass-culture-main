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
        {'Primary Button'}
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
        {'Secondary Button'}
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

  const tertiaryLink = (
    <div className="flex-block">
      <a
        className="tertiary-link"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        <span>
          {'Tertiary Link'}
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

  const quaternaryLink = (
    <div className="flex-block">
      <a
        className="quaternary-link"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        <span>
          {'Quaternary Link'}
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
      {tertiaryLink}
      <hr />
      {quaternaryLink}
      <br />
    </div>
  )
}

export default StyleguideButtons
