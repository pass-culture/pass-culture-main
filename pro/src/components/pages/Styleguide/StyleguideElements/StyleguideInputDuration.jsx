import React from 'react'

import DurationInput from 'components/layout/inputs/DurationInput/DurationInput'

const StyleguideInputDuration = () => {
  const inputDurationEnabled = `
    <DurationInput
      label="Intitulé"
      name="input-time-default"
      onChange={onChange}
      subLabel="Intitulé secondaire"
      value="60"
    />
  `
  const inputDurationReadOnly = `
    <DurationInput
      label="Intitulé"
      name="input-time-default"
      onChange={onChange}
      readOnly
      subLabel="Intitulé secondaire"
      value="60"
    />
  `

  const inputDurationWithError = `
    <DurationInput
      error="Message d'erreur"
      label="Intitulé"
      name="input-text-disabled"
      subLabel="Intitulé secondaire"
      value="60"
    />
  `

  function onChange() {
    console.log('OnChange input text')
  }

  return (
    <div>
      <h3>Champs de durée</h3>
      <div className="flex-block">
        <DurationInput
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          subLabel="Intitulé secondaire"
          value="60"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputDurationEnabled}</code>
          </pre>
        </div>
      </div>
      <br />
      <h3>Champs de durée read only</h3>
      <div className="flex-block">
        <DurationInput
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          readOnly
          subLabel="Intitulé secondaire"
          value="60"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputDurationReadOnly}</code>
          </pre>
        </div>
      </div>
      <br />
      <hr />
      <h3>Champs de durée en erreur</h3>
      <div className="flex-block">
        <DurationInput
          error="Ce champs comporte une erreur"
          label="Intitulé"
          name="input-time-default"
          onChange={onChange}
          subLabel="Intitulé secondaire"
          value="60"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{inputDurationWithError}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideInputDuration
