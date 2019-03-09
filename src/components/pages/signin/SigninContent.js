/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'
import { requestData } from 'redux-saga-data'

import FormInputs from './FormInputs'
import FormHeader from './FormHeader'

import { FormFooter } from '../../forms'
import { parseSubmitErrors } from '../../forms/utils'

const submitButtonOptions = {
  className: 'is-bold is-white-text',
  id: 'signin-submit-button',
  label: 'Connexion',
}

class Signin extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { isloading: false }
  }

  handleRequestFail = formResolver => (state, action) => {
    // on retourne les erreurs API au formulaire
    const nextstate = { isloading: false }
    const {
      payload: { errors },
    } = action

    const errorsByKey = parseSubmitErrors(errors)
    this.setState(nextstate, () => formResolver(errorsByKey))
  }

  handleRequestSuccess = formResolver => () => {
    const { history, query } = this.props
    const nextstate = { isloading: false }
    const queryParams = query.parse()
    this.setState(nextstate, () => {
      formResolver()
      const nextUrl = queryParams.from
        ? decodeURIComponent(queryParams.from)
        : '/decouverte'
      history.push(nextUrl)
    })
  }

  onFormSubmit = formValues => {
    const routeMethod = 'POST'
    const routePath = '/users/signin'
    const { dispatch } = this.props
    this.setState({ isloading: true })
    // NOTE: on retourne une promise au formulaire
    // pour pouvoir gérer les erreurs de l'API
    // directement dans les champs du formulaire
    const formSubmitPromise = new Promise(resolve => {
      const config = {
        apiPath: routePath,
        body: { ...formValues },
        handleFail: this.handleRequestFail(resolve),
        handleSuccess: this.handleRequestSuccess(resolve),
        method: routeMethod,
      }
      dispatch(requestData(config))
    })
    return formSubmitPromise
  }

  render() {
    const { isloading } = this.state
    return (
      <div id="sign-in-page" className="page pc-gradient is-relative">
        <Form
          onSubmit={this.onFormSubmit}
          render={({
            dirtySinceLastSubmit,
            handleSubmit,
            hasSubmitErrors,
            hasValidationErrors,
            pristine,
          }) => {
            const canSubmit =
              (!pristine &&
                !hasSubmitErrors &&
                !hasValidationErrors &&
                !isloading) ||
              (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
            return (
              <form
                noValidate
                autoComplete="off"
                disabled={isloading}
                onSubmit={handleSubmit}
                className="pc-final-form flex-rows is-full-layout"
              >
                <div className="flex-1 flex-rows flex-center is-white-text padded-2x overflow-y">
                  <FormHeader />
                  <FormInputs />
                </div>
                <FormFooter
                  cancel={false}
                  submit={{ ...submitButtonOptions, disabled: !canSubmit }}
                />
              </form>
            )
          }}
        />
      </div>
    )
  }
}

Signin.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  query: PropTypes.object.isRequired,
}

export default Signin
