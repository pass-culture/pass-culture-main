import React, { useCallback, useState } from 'react'

import CheckboxInput from 'components/layout/inputs/CheckboxInput'

const StyleguideCheckboxes = () => {
  const [checked, setChecked] = useState(false)

  const checkboxeSnippet = String.raw`
    <CheckboxInput
      onChange={handleOnChange}
      value="checkbox_value"
      name="checkbox_name"
      label="Checkbox label"
      checked={checked}
    />
  `

  const handleOnChange = useCallback(
    () => setChecked(() => !checked),
    [checked]
  )

  return (
    <div className="styleguide-select">
      <div className="flex-block">
        <CheckboxInput
          checked={checked}
          label="Checkbox label"
          name="checkbox_name"
          onChange={handleOnChange}
          value="checkbox_value"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{checkboxeSnippet}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideCheckboxes
