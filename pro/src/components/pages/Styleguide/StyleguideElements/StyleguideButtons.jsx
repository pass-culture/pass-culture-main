import React, { useCallback, useState } from 'react'

import Icon from 'components/layout/Icon'
import { SubmitButton } from 'ui-kit'

const StyleguideButtons = () => {
  const primaryButton = (
    <div className="flex-block">
      <button className="primary-link" type="button">
        Primary Button
      </button>
      <div>
        classe
        <span className="class-name">{' .primary-button '}</span>
        (boutons) ou
        <span className="class-name">{' .primary-link '}</span>
        (liens)
      </div>
    </div>
  )

  const secondaryButton = (
    <div className="flex-block">
      <button className="secondary-button" type="button">
        Secondary Button
      </button>
      <div>
        classe
        <span className="class-name">{' .secondary-button '}</span>
        (boutons) ou
        <span className="class-name">{' .secondary-link '}</span>
        (liens)
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
        <span>Tertiary Link</span>
      </a>
      <div>
        classe
        <span className="class-name">{' .tertiary-link '}</span>
        (liens)
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
        <span>Quaternary Link</span>
      </a>
      <div>
        classe
        <span className="class-name">{' .quaternary-link '}</span>
        (liens)
      </div>
    </div>
  )

  const submitButtonSnippet = `
    <SubmitButton
        className={className}
        disabled={disabled}
        onClick={onClick}
        isLoading={isLoading}
    >
      {"Valeur"}
    </SubmitButton>
  `
  const [isLoading, setIsLoading] = useState()
  const handleOnClick = useCallback(() => setIsLoading(true), [])
  const SubmitButtonSample = (
    <div className="flex-block">
      <SubmitButton isLoading={isLoading} onClick={handleOnClick}>
        Submit Button
      </SubmitButton>
      <div className="it-description">
        <pre className="it-icon-snippet">
          <code>{submitButtonSnippet}</code>
        </pre>
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
      <hr />
      {SubmitButtonSample}
      <br />
    </div>
  )
}

export default StyleguideButtons
