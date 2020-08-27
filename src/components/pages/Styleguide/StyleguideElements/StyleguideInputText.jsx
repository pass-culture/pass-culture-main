import React from 'react'
import TextInput from '../../../layout/inputs/TextInput/TextInput'
import TextInputWithIcon from '../../../layout/inputs/TextInputWithIcon/TextInputWithIcon'

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

  function onClick() {
    console.log('OnClick icon input')
  }

  function onChange() {
    console.log('OnChange input text')
  }

  return (
    <div>
      <h3>
        {'Input Text - Default'}
      </h3>
      <div className="flex-block">
        <TextInput
          label="Intitulé"
          name="input-text-default"
          onChange={onChange}
          placeholder="placeholder"
          required
          sublabel="Intitulé secondaire"
          type="text"
        />
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
        <TextInput
          disabled
          label="Intitulé"
          name="input-text-disabled"
          placeholder="placeholder disabled"
          sublabel="Intitulé secondaire"
          type="text"
        />
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
          <TextInputWithIcon
            icon="ico-search"
            iconAlt="alt-for-icon"
            label="Intitulé"
            name="input-text-icon-default"
            onChange={onChange}
            onClick={onClick}
            placeholder="placeholder with icon"
            sublabel="Intitulé secondaire"
            type="text"
          />
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
          <TextInputWithIcon
            disabled
            icon="ico-search"
            iconAlt="alt-for-icon"
            label="Intitulé"
            name="input-text-icon-disabled"
            placeholder="placeholder with icon"
            sublabel="Intitulé secondaire"
            type="text"
          />
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
