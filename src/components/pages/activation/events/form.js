/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { withRouter } from 'react-router-dom'

import Spinner from '../../../layout/Spinner'
import { canSubmitForm } from '../utils'
import { SelectBox } from '../../../forms/inputs'

const onFormSubmit = history => formValues => {
  const { event } = formValues
  const nexturl = `/decouverte/${event.value}`
  history.push(nexturl)
}

const ActivationFormWrapper = ({ history, isLoading, offers }) => (
  <React.Fragment>
    {isLoading && <Spinner />}
    {!isLoading && (
      <Form
        initialValues={{}}
        onSubmit={onFormSubmit(history)}
        render={({ handleSubmit, ...rest }) => {
          const canSubmit = !isLoading && canSubmitForm(rest)
          return (
            <form
              noValidate
              autoComplete="off"
              disabled={isLoading}
              onSubmit={handleSubmit}
            >
              <SelectBox
                format={{ value: 'id' }}
                name="event"
                provider={offers}
                placeholder="Choisissez une ville"
              />
              <button type="submit" disabled={!canSubmit}>
                <span>Suite</span>
              </button>
            </form>
          )
        }}
      />
    )}
  </React.Fragment>
)

ActivationFormWrapper.propTypes = {
  history: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
  offers: PropTypes.array.isRequired,
}

export default withRouter(ActivationFormWrapper)
