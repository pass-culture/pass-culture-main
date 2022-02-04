import React from 'react'

import TextareaInput from 'components/layout/inputs/TextareaInput'

const StyleguideInputTextarea = () => {
  const inputTextareaEnabled = `
    <TextareaInput
      label="Intitulé"
      name="input-text-default"
      onChange={onChange}
      placeholder="placeholder"
      required
      subLabel="Intitulé secondaire"
      value="Valeur"
    />
  `

  const inputTextareaWithError = `
    <TextareaInput
      error="Ce champs comporte une erreur"
      label="Intitulé"
      name="input-text-default"
      onChange={onChange}
      placeholder="placeholder"
      required
      subLabel="Intitulé secondaire"
    />
  `
  const inputTextareaDisabled = `
    <TextareaInput
      disabled
      label="Intitulé"
      name="input-text-disabled"
      placeholder="placeholder disabled"
      subLabel="Intitulé secondaire"
      value="Valeur"
    />
  `

  const inputTextareaWithCaracterCount = `
    <TextareaInput
      countCharacters
      label="Intitulé"
      maxLength={20}
      name="input-text-with-character-count"
      onChange={onChange}
      placeholder="placeholder"
      required
      subLabel="Intitulé secondaire"
      value="Valeur"
    />
  `

  function onChange() {
    console.log('OnChange input text')
  }

  return (
    <div>
      <h3>Champs textuel</h3>
      <div className="flex-block">
        <div className="it-content">
          <TextareaInput
            label="Intitulé"
            name="input-text-default"
            onChange={onChange}
            placeholder="placeholder"
            required
            subLabel="Intitulé secondaire"
          />
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputTextareaEnabled}</code>
          </pre>
        </div>
      </div>
      <br />
      <div className="flex-block">
        <div className="it-content">
          <TextareaInput
            disabled
            label="Intitulé"
            name="input-text-disabled"
            placeholder="placeholder disabled"
            subLabel="Intitulé secondaire"
          />
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputTextareaDisabled}</code>
          </pre>
        </div>
      </div>
      <hr />
      <h3>Champs textuel en erreur</h3>
      <div className="flex-block">
        <div className="it-content">
          <TextareaInput
            error="Ce champs comporte une erreur"
            label="Intitulé"
            name="input-text-default"
            onChange={onChange}
            placeholder="placeholder"
            required
            subLabel="Intitulé secondaire"
          />
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputTextareaWithError}</code>
          </pre>
        </div>
      </div>
      <br />
      <h3>Champs avec compte de caractères</h3>
      <div className="flex-block">
        <div className="it-content">
          <TextareaInput
            countCharacters
            label="Intitulé"
            maxLength={20}
            name="input-text-with-character-count"
            onChange={onChange}
            placeholder="placeholder"
            required
            subLabel="Intitulé secondaire"
          />
        </div>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputTextareaWithCaracterCount}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideInputTextarea
