import React, { useState } from 'react'
import Select from '../../../layout/inputs/Select'

const StyleguideSelect = () => {
  const [selectedValueId, setSelectedValueId] = useState(1)

  const selectSnippet = String.raw`
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
            <code>
              {selectSnippet}
            </code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideSelect
