import React from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import TextInputWithIcon from 'components/layout/inputs/TextInputWithIcon/TextInputWithIcon'

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
      value="Valeur"
    />
  `

  const inputTextWithError = String.raw`
    <TextInput
      error="Ce champs comporte une erreur"
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
      value="Valeur"
    />
  `

  const inputWithIconEnabled = String.raw`
    <TextInputWithIcon
      icon="ico-search"
      iconAlt="alt-for-icon"
      label="Intitulé"
      name="input-text-icon-default"
      onChange={onChange}
      onIconClick={onClick}
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

  const inputWithErrorMessage = String.raw`
    <TextInputWithIcon
      error="La saisie du champs n'est pas correcte"
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
        {'Champs textuel'}
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
        {'Champs textuel en erreur'}
      </h3>
      <div className="flex-block">
        <TextInput
          error="Ce champs comporte une erreur"
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
              {inputTextWithError}
            </code>
          </pre>
        </div>
      </div>
      <h3>
        {'Champs textuel avec icône'}
      </h3>
      <div className="flex-block">
        <div>
          <TextInputWithIcon
            icon="ico-search"
            iconAlt="alt-for-icon"
            label="Intitulé"
            name="input-text-icon-default"
            onChange={onChange}
            onIconClick={onClick}
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
      <hr />
      <h3>
        {'Champs avec icône en erreur'}
      </h3>
      <div className="flex-block">
        <div>
          <TextInputWithIcon
            error={"La saisie n'est pas correcte"}
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
              {inputWithErrorMessage}
            </code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideInputText
