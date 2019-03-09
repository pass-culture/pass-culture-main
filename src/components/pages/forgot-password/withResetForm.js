/* eslint
    react/jsx-one-expression-per-line: 0 */
// import { FORM_ERROR } from 'final-form'
import PropTypes from 'prop-types'
import React from 'react'
import { Form as FinalForm } from 'react-final-form'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { requestData } from 'redux-saga-data'

const noop = () => {}

const withPasswordForm = (
  WrappedComponent,
  validator,
  routePath,
  routeMethod
) => {
  const name = WrappedComponent.displayName || 'Component'
  withPasswordForm.displayName = `withPasswordForm(${name})`

  // azertyazertyP1$
  class ResetPasswordForm extends React.PureComponent {
    constructor(props) {
      super(props)
      const { dispatch, initialValues } = this.props
      this.state = { isloading: false }
      this.initialValues = { ...initialValues }
      this.actions = bindActionCreators({ requestData }, dispatch)
    }

    handleRequestFail = formResolver => (state, action) => {
      // on retourne les erreurs API au formulaire
      const nextstate = { isloading: false }
      const {
        payload: { errors },
      } = action
      this.setState(nextstate, () => formResolver(errors))
    }

    handleRequestSuccess = formResolver => () => {
      const { history, location } = this.props
      const nextstate = { isloading: false }
      this.setState(nextstate, () => {
        formResolver()
        const baseurl = location.pathname
        const nexturl = `${baseurl}/success${location.search}`
        history.replace(nexturl)
      })
    }

    onFormSubmit = formValues => {
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
        this.actions.requestData(config)
      })
      return formSubmitPromise
    }

    render() {
      const { isloading } = this.state
      return (
        <FinalForm
          validate={validator || noop}
          onSubmit={this.onFormSubmit}
          initialValues={this.initialValues || {}}
          render={({
            // https://github.com/final-form/final-form#formstate
            dirtySinceLastSubmit,
            error: preSubmitError,
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
                className="pc-final-form is-full-layout"
              >
                <WrappedComponent
                  {...this.props}
                  canSubmit={canSubmit}
                  isLoading={isloading}
                  formErrors={!pristine && preSubmitError}
                />
              </form>
            )
          }}
        />
      )
    }
  }

  ResetPasswordForm.defaultProps = {
    initialValues: {},
  }

  ResetPasswordForm.propTypes = {
    dispatch: PropTypes.func.isRequired,
    // NOTE: history et location sont automatiquement
    // injectées par le render de la route du react-router-dom
    history: PropTypes.object.isRequired,
    initialValues: PropTypes.object,
    location: PropTypes.object.isRequired,
  }

  return connect()(ResetPasswordForm)
}

export default withPasswordForm
