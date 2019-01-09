/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { withRouter } from 'react-router-dom'

import Spinner from '../../../layout/Spinner'
import { canSubmitForm } from '../utils'
import { SelectBox } from '../../../forms/inputs'

class ActivationEventsForm extends React.PureComponent {
  onFormSubmit = formValues => {
    const { event } = formValues
    const { history } = this.props
    const nexturl = `${event.url}?to=verso`
    history.push(nexturl)
  }

  renderEventsSelectbox = () => {
    const { offers } = this.props
    return (
      <SelectBox
        name="event"
        provider={offers}
        menuPlacement="top"
        isClearable={false}
        maxMenuHeight={200}
        isSearchable={false}
        placeholder="Choisissez une ville"
      />
    )
  }

  renderSubmitButton = canSubmit => (
    <p className="clearfix mt18">
      <button
        type="submit"
        disabled={!canSubmit}
        id="activation-events-submit-button"
        className="button is-rounded is-medium float-right"
      >
        <span>Suite</span>
      </button>
    </p>
  )

  render() {
    const { isLoading } = this.props
    return (
      <React.Fragment>
        {isLoading && <Spinner />}
        {!isLoading && (
          <Form
            initialValues={{}}
            onSubmit={this.onFormSubmit}
            render={({ handleSubmit, ...rest }) => {
              const canSubmit = !isLoading && canSubmitForm(rest)
              return (
                <form
                  noValidate
                  autoComplete="off"
                  disabled={isLoading}
                  onSubmit={handleSubmit}
                >
                  {this.renderEventsSelectbox()}
                  {this.renderSubmitButton(canSubmit)}
                </form>
              )
            }}
          />
        )}
      </React.Fragment>
    )
  }
}

ActivationEventsForm.propTypes = {
  history: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
  offers: PropTypes.array.isRequired,
}

export default withRouter(ActivationEventsForm)
