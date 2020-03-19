import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form as FinalForm } from 'react-final-form'
import { requestData } from 'redux-thunk-data'
import { resolveCurrentUser } from '../../../hocs/with-login/with-react-redux-login'

import parseSubmitErrors from '../../../forms/utils/parseSubmitErrors'
import Header from '../../../layout/Header/Header'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

class ProfileForm extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { isLoading: false }
  }

  handleRequestFail = formResolver => (state, action) => {
    const nextState = { isLoading: false }
    const {
      payload: { errors },
    } = action
    const errorsByKey = parseSubmitErrors(errors)
    this.setState(nextState, () => {
      formResolver(errorsByKey)
    })
  }

  handleRequestSuccess = formResolver => () => {
    const { history, location } = this.props
    const nextState = { isLoading: false }

    this.setState(nextState, () => {
      formResolver()
      const redirectUrl = `${location.pathname}/success`
      history.replace(redirectUrl)
    })
  }

  handleOnFormSubmit = formValues => {
    this.setState({ isLoading: true })
    const {
      config: { routePath, routeMethod, stateKey },
      dispatch,
    } = this.props

    return new Promise(resolve => {
      const config = {
        apiPath: routePath,
        body: { ...formValues },
        handleFail: this.handleRequestFail(resolve),
        handleSuccess: this.handleRequestSuccess(resolve),
        method: routeMethod,
        resolve: resolveCurrentUser,
      }

      if (stateKey) {
        config.key = stateKey
      }

      dispatch(requestData(config))
    })
  }

  handleOnFormReset = () => {
    const { history } = this.props
    history.goBack()
  }

  renderFinalForm = ({
    dirtySinceLastSubmit,
    error: preSubmitError,
    handleSubmit,
    hasSubmitErrors,
    hasValidationErrors,
    pristine,
  }) => {
    const { WrappedComponent, title } = this.props
    const { isLoading } = this.state
    const canSubmit =
      (!pristine && !hasSubmitErrors && !hasValidationErrors && !isLoading) ||
      (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
    return (
      <form
        autoComplete="off"
        className="mosaic-background form flex-rows"
        noValidate
        onReset={this.handleOnFormReset}
        onSubmit={handleSubmit}
      >
        <Header
          backTo="/profil"
          closeTo={null}
          isLoading={isLoading}
          submitDisabled={canSubmit}
          title={title}
          useSubmit
        />
        <div className="py30 px12">
          <WrappedComponent
            {...this.props}
            formErrors={!pristine && preSubmitError}
            isLoading={isLoading}
          />
        </div>
      </form>
    )
  }

  render() {
    const { initialValues, validator } = this.props
    const { isLoading } = this.state

    return (
      <div className="pc-page-view flex-rows with-header">
        <FinalForm
          initialValues={initialValues}
          onSubmit={this.handleOnFormSubmit}
          render={this.renderFinalForm}
          validate={validator}
        />
        <RelativeFooterContainer
          disabled={isLoading}
          extraClassName="dotted-top-red"
          theme="white"
        />
      </div>
    )
  }
}

ProfileForm.defaultProps = {
  title: null,
  validator: () => {},
}

ProfileForm.propTypes = {
  WrappedComponent: PropTypes.elementType.isRequired,
  config: PropTypes.shape().isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  initialValues: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  title: PropTypes.string,
  validator: PropTypes.func,
}

export default ProfileForm
