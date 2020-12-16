import React from 'react'

import TimeInput from 'components/layout/inputs/TimeInput'

const StyleguideInputText = () => {
  const inputTimeEnabled = `
    <TimeInput
      label="Intitulé"
      name="input-time-default"
      onChange={onChange}
      subLabel="Intitulé secondaire"
      value="01:00"
    />
  `
  const inputTimeReadOnly = `
    <TimeInput
      label="Intitulé"
      name="input-time-default"
      onChange={onChange}
      readOnly
      subLabel="Intitulé secondaire"
      value="01:00"
    />
  `

  const inputTimeWithError = `
    <TextInput
      disabled
      label="Intitulé"
      name="input-text-disabled"
      placeholder="placeholder disabled"
      subLabel="Intitulé secondaire"
      type="text"
      value="01:00"

    <TimeInput
      error="Message d'erreur"
      label="Intitulé"
      name="input-text-disabled"
      subLabel="Intitulé secondaire"
      value="01:00"
    />
  `

  function onChange() {
    console.log('OnChange input text')
  }

  return (
    <div>
      <h3>
        {'Champs de durée'}
      </h3>
      <div className="flex-block">
        <TimeInput
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          subLabel="Intitulé secondaire"
          value="01:00"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputTimeEnabled}
            </code>
          </pre>
        </div>
      </div>
      <br />
      <h3>
        {'Champs de durée read only'}
      </h3>
      <div className="flex-block">
        <TimeInput
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          readOnly
          subLabel="Intitulé secondaire"
          value="01:00"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputTimeReadOnly}
            </code>
          </pre>
        </div>
      </div>
      <br />
      <hr />
      <h3>
        {'Champs de durée en erreur'}
      </h3>
      <div className="flex-block">
        <TimeInput
          error="Ce champs comporte une erreur"
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          subLabel="Intitulé secondaire"
          value="01:00"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {inputTimeWithError}
            </code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideInputText
