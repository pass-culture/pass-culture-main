import React from 'react'
import { Field } from 'react-final-form'

const required = value => {
  return value ? undefined : 'Ce champs est requis'
}

const Name = () => (
  <Field
    name="name"
    validate={required}
  >
    {({ input }) => {
      return (
        <div className="field text-field is-label-aligned">
          <label
            className="field-label"
            htmlFor="offerer__designation"
          >
            {'Désignation : '}
          </label>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div className="field-inner flex-columns items-center">
                <input
                  className="input is-normal"
                  id="offerer__designation"
                  readOnly
                  type="text"
                  {...input}
                />
              </div>
            </div>
          </div>
        </div>
      )
    }}
  </Field>
)

export default Name
