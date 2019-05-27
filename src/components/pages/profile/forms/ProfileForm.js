import PropTypes from 'prop-types'
import React from 'react'
import { Form as FinalForm } from 'react-final-form'
import { requestData } from 'redux-saga-data'

import { ROOT_PATH } from '../../../../utils/config'
import { parseSubmitErrors } from '../../../forms/utils'
import PageHeader from '../../../layout/PageHeader'
import NavigationFooter from '../../../layout/NavigationFooter'

const BACKGROUND_IMAGE = `url('${ROOT_PATH}/mosaic-k.png')`

class ProfileForm extends React.PureComponent {
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
    this.setState(nextState, () => formResolver(errorsByKey))
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

  onFormSubmit = formValues => {
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
        isMergingDatum: true,
        method: routeMethod,
      }

      if (stateKey) {
        config.key = stateKey
      }

      dispatch(requestData(config))
    })
  }

  onFormReset = () => {
    const { history } = this.props
    history.goBack()
  }

  render() {
    const { WrappedComponent, initialValues, title, validator } = this.props
    const { isLoading } = this.state
    return (
      <div
        id="profile-page-form-view"
        className="pc-page-view pc-theme-default flex-rows"
      >
        <FinalForm
          validate={validator}
          onSubmit={this.onFormSubmit}
          initialValues={initialValues}
          render={({
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
                !isLoading) ||
              (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
            return (
              <form
                noValidate
                autoComplete="off"
                onSubmit={handleSubmit}
                onReset={this.onFormReset}
                className="pc-final-form flex-rows"
              >
                <PageHeader
                  useBack
                  useSubmit
                  theme="red"
                  canSubmit={canSubmit}
                  isLoading={isLoading}
                  title={title}
                />
                <main
                  role="main"
                  style={{ backgroundImage: BACKGROUND_IMAGE }}
                  className="pc-main is-clipped is-relative flex-1"
                >
                  <WrappedComponent
                    {...this.props}
                    isLoading={isLoading}
                    formErrors={!pristine && preSubmitError}
                  />
                </main>
              </form>
            )
          }}
        />
        <NavigationFooter
          theme="white"
          disabled={isLoading}
          className="dotted-top-red"
        />
      </div>
    )
  }
}

ProfileForm.defaultProps = {
  title: null,
}

ProfileForm.propTypes = {
  WrappedComponent: PropTypes.elementType.isRequired,
  config: PropTypes.object.isRequired,
  currentUser: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  initialValues: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  title: PropTypes.string,
  validator: PropTypes.func.isRequired,
}

export default ProfileForm
