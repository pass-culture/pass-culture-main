import React, { useState } from 'react'

import Select from 'components/layout/inputs/Select'

const StyleguideSelect = () => {
  const [selectedValueId, setSelectedValueId] = useState(1)

  const selectSnippet = `
    const defaultOption = {
      id: 1,
      displayName: 'Option par défaut'
    }

    const options = [
      {
        id: 2,
        displayName: 'Option 1'
      },
      {
        id: 3,
        displayName: 'Option 2'
      }
    ]

    <Select
      label="Liste déroulante"
      handleSelection={handleOnChange}
      defaultOption={defaultOption}
      selectedValue={selectedValueId}
      name="select"
      options={options}
    />
  `
  const selectWithErrorSnippet = `
    const defaultOption = {
      id: 1,
      displayName: 'Option par défaut'
    }

    <Select
      error="Ce champs comporte une erreur"
      label="Liste déroulante avec une erreur"
      handleSelection={handleOnChange}
      defaultOption={defaultOption}
      selectedValue={selectedValueId}
      name="select"
      options={[]}
    />
  `
  const defaultOption = {
    id: 1,
    displayName: 'Option par défaut',
  }

  const options = [
    {
      id: 2,
      displayName: 'Option 1',
    },
    {
      id: 3,
      displayName: 'Option 2',
    },
  ]

  function handleOnChange(event) {
    setSelectedValueId(event.target.value)
  }

  return (
    <div className="styleguide-select">
      <h3>Select</h3>
      <div className="flex-block">
        <Select
          defaultOption={defaultOption}
          handleSelection={handleOnChange}
          label="Liste déroulante"
          name="select"
          options={options}
          selectedValue={selectedValueId}
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{selectSnippet}</code>
          </pre>
        </div>
      </div>
      <h3>Select en erreur</h3>
      <div className="flex-block">
        <Select
          defaultOption={defaultOption}
          error="Ce champs comporte une erreur"
          handleSelection={handleOnChange}
          label="Liste déroulante"
          name="select"
          options={options}
          selectedValue={selectedValueId}
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{selectWithErrorSnippet}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideSelect
