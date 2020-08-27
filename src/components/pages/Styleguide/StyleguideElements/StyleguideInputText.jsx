import React from 'react'
import TextInput from '../../../layout/inputs/TextInput/TextInput'
import TextInputWithIcon from '../../../layout/inputs/TextInputWithIcon/TextInputWithIcon'

const StyleguideInputText = () => {
  const inputTextEnabled = String.raw`
    <TextInput
      label="Intitulé"
      name="input-text-default"
      onChange={onChange}
      placeholder="placeholder"
      required
      sublabel="Intitulé secondaire"
      type="text"
    />
  `

  const inputTextDisabled = String.raw`
    <TextInput
      disabled
      label="Intitulé"
      name="input-text-disabled"
      placeholder="placeholder disabled"
      sublabel="Intitulé secondaire"
      type="text"
    />
  `

  const inputWithIconEnabled = String.raw`
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
   `

  const inputWithIconDisabled = String.raw`
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
        {'Text Input - Default'}
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
        {'Text Input - With Icon'}
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
