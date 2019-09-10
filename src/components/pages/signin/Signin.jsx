import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'

import FormInputs from './FormInputs'
import FormHeader from './FormHeader'
import canSubmitForm from './canSubmitForm'

import { FormFooter } from '../../forms'
import { parseSubmitErrors } from '../../forms/utils'

const submitButtonOptions = {
  className: 'is-bold is-white-text',
  id: 'signin-submit-button',
  label: 'Connexion',
}

const signUpLinkOption = {
  className: 'is-white-text',
  id: 'sign-up-link',
  label: 'Créer un compte',
  target: '_blank',
  url: 'https://www.demarches-simplifiees.fr/commencer/inscription-pass-culture',
}

class Signin extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleRequestFail = formResolver => (state, action) => {
    // on retourne les erreurs API au formulaire
    const nextstate = { isLoading: false }
    const {
      payload: { errors },
    } = action

    const errorsByKey = parseSubmitErrors(errors)
    this.setState(nextstate, () => formResolver(errorsByKey))
  }

  handleRequestSuccess = formResolver => () => {
    const { history, query } = this.props
    const nextstate = { isLoading: false }
    const queryParams = query.parse()
    this.setState(nextstate, () => {
      formResolver()
      const nextUrl = queryParams.from ? decodeURIComponent(queryParams.from) : '/decouverte'
      history.push(nextUrl)
    })
  }

  handleOnFormSubmit = formValues => {
    const { submitSigninForm } = this.props

    this.setState({ isLoading: true })

    return submitSigninForm(formValues, this.handleRequestFail, this.handleRequestSuccess)
  }

  renderForm = formProps => {
    const { isLoading } = this.state
    const canSubmit = !isLoading && canSubmitForm(formProps)
    const { handleSubmit } = formProps
    return (
      <form
        autoComplete="off"
        className="pc-final-form flex-rows is-full-layout"
        disabled={isLoading}
        noValidate
        onSubmit={handleSubmit}
      >
        <div className="flex-1 flex-rows flex-center is-white-text padded-2x overflow-y">
          <FormHeader />
          <FormInputs />
        </div>
        <FormFooter
          externalLink={signUpLinkOption}
          submit={{ ...submitButtonOptions, disabled: !canSubmit }}
        />
      </form>
    )
  }

  render() {
    return (
      <div
        className="page pc-gradient is-relative"
        id="sign-in-page"
      >
        <Form
          onSubmit={this.handleOnFormSubmit}
          render={this.renderForm}
        />
      </div>
    )
  }
}

Signin.propTypes = {
  history: PropTypes.shape().isRequired,
  query: PropTypes.shape().isRequired,
  submitSigninForm: PropTypes.func.isRequired,
}

export default Signin
