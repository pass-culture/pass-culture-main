import React from 'react'
import { Field } from 'react-final-form'

const City = () => (
  <Field name="city">
    {({ input }) => {
      return (
        <div className="field text-field is-label-aligned">
          <label
            className="field-label"
            htmlFor="city"
          >
            {'Ville : '}
          </label>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div className="field-inner flex-columns items-center">
                <input
                  className="input is-normal"
                  id="city"
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

export default City
