import React from 'react'
import { Field } from 'react-final-form'

const Address = () => (
  <Field name="address">
    {({ input }) => {
      return (
        <div className="field text-field is-label-aligned">
          <label
            className="field-label"
            htmlFor="offerer__address"
          >
            {'Siège social : '}
          </label>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div className="field-inner flex-columns items-center">
                <input
                  className="input is-normal"
                  id="offerer__address"
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

export default Address
