import React from 'react'
import Icon from '../../layout/Icon'

const StyleguideInputText = () => {
  const inputTextEnabled = String.raw`
    <label className="input-text">
      {'Intitulé'}
      <span className="it-sub-label">
        {'Intitulé secondaire'}
      </span>
      <input className="it-input" />
    </label>
  `

  const inputTextDisabled = String.raw`
    <label className="input-text">
      {'Intitulé'}
      <span className="it-sub-label">
        {'Intitulé secondaire'}
      </span>
      <input
        className="it-input"
        disabled
      />
    </label>
  `

  const inputWithIconEnabled = String.raw`
  <label className="input-text"}>
    {'Intitulé'}
    <span className="it-sub-label">
      {'Intitulé secondaire'}
    </span>
    <div className="it-with-icon-container">
      <input className="it-input-with-icon" />
      <button className="it-icon">
        <Icon svg="ico-search" />
      </button>
    </div>
  </label>
   `

  const inputWithIconDisabled = String.raw`
  <label className="input-text"}>
    {'Intitulé'}
    <span className="it-sub-label">
      {'Intitulé secondaire'}
    </span>
    <div className="it-with-icon-container disabled">
      <input
        className="it-with-icon"
        disabled
       />
      <button className="it-icon">
        <Icon svg="ico-search" />
      </button>
    </div>
  </label>
  `

  return (
    <div>
      <h3>
        {'Input Text - Default'}
      </h3>
      <div className="flex-block">
        <label className="input-text">
          {'Intitulé'}
          <span className="it-sub-label">
            {'Intitulé secondaire'}
          </span>
          <input
            className="it-input"
            name="input-enabled"
            placeholder="placeholder"
            type="text"
          />
        </label>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputTextEnabled}
            </code>
          </pre>
        </div>
      </div>
      <br />
      <div className="flex-block">
        <label className="input-text">
          {'Intitulé'}
          <span className="it-sub-label">
            {'Intitulé secondaire'}
          </span>
          <input
            className="it-input"
            disabled
            name="input-disabled"
            placeholder="placeholder disabled"
            type="text"
          />
        </label>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputTextDisabled}
            </code>
          </pre>
        </div>
      </div>
      <hr />
      <h3>
        {'Input Text - With Icon'}
      </h3>
      <div className="flex-block">
        <div>
          <label className="input-text">
            {'Intitulé'}
            <span className="it-sub-label">
              {'Intitulé secondaire'}
            </span>
            <div className="it-with-icon-container">
              <input
                className="it-input-with-icon"
                name="input-with-icon"
                placeholder="placeholder with icon"
                type="text"
              />
              <button
                className="it-icon"
                type="button"
              >
                <Icon svg="ico-search" />
              </button>
            </div>
          </label>
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputWithIconEnabled}
            </code>
          </pre>
        </div>
      </div>
      <br />
      <div className="flex-block">
        <div>
          <label className="input-text">
            {'Intitulé'}
            <span className="it-sub-label">
              {'Intitulé secondaire'}
            </span>
            <div className="it-with-icon-container disabled">
              <input
                className="it-input-with-icon"
                disabled
                name="input-with-icon"
                placeholder="placeholder with icon"
                type="text"
              />
              <button
                className="it-icon"
                type="button"
              >
                <Icon svg="ico-search" />
              </button>
            </div>
          </label>
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputWithIconDisabled}
            </code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideInputText
