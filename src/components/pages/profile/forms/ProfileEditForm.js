/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'pass-culture-shared'
import { bindActionCreators, compose } from 'redux'
import { Form as FinalForm } from 'react-final-form'

import { fields } from '../page-config'
import { ROOT_PATH } from '../../../../utils/config'
import { InputField } from '../../../forms/inputs'
import PageHeader from '../../../layout/PageHeader'
import NavigationFooter from '../../../layout/NavigationFooter'

const parseSubmitErrors = errors =>
  Object.keys(errors).reduce((acc, key) => {
    // FIXME -> test avec un array d'erreurs
    // a deplacer dans un tests unitaires
    // const err = errors[key].concat('toto')
    const err = errors[key]
    return { ...acc, [key]: err }
  }, {})

class ProfileEditForm extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch, user } = this.props
    // initialValues sont detruites a chaque mount/unmount
    this.initialValues = Object.assign({}, user)
    this.state = { isloading: false }
    this.actions = bindActionCreators({ requestData }, dispatch)
  }

  handleRequestFail = formResolver => (state, action) => {
    // on retourne les erreurs API au formulaire
    const nextstate = { isloading: false }
    const errors = parseSubmitErrors(action.errors)
    this.setState(nextstate, () => formResolver(errors))
  }

  handleRequestSuccess = () => {
    const { history, location } = this.props
    const nextlocation = `${location.pathname}/success`
    const nextstate = { isloading: false }
    this.setState(nextstate, () => history.replace(nextlocation))
  }

  onFormSubmit = formValues => {
    this.setState({ isloading: true }, () => {
      const route = 'users/current'
      this.actions.requestData('PATCH', route, {
        body: { ...formValues },
        handleFail: this.handleRequestFail,
        handleSuccess: this.handleRequestSuccess,
        key: 'user',
      })
    })
  }

  onFormReset = () => {
    const { history } = this.props
    history.goBack()
  }

  render() {
    const { isloading } = this.state
    const { match } = this.props
    const { view } = match.params
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    const config = fields[view]
    const defaultValue = this.initialValues[config.key]
    return (
      <div
        id="profile-page-edit-view"
        className="pc-page-view pc-theme-default flex-rows"
      >
        <FinalForm
          // validate={validatePasswordForm}
          onSubmit={this.onFormSubmit}
          initialValues={this.initialValues || {}}
          render={({
            // https://github.com/final-form/final-form#formstate
            dirtySinceLastSubmit,
            // error: preSubmitError,
            handleSubmit,
            hasSubmitErrors,
            hasValidationErrors,
            pristine,
          }) => {
            const canSubmit =
              (!hasSubmitErrors && !hasValidationErrors && !isloading) ||
              (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
            return (
              <form
                noValidate
                autoComplete="off"
                disabled={isloading}
                onSubmit={handleSubmit}
                onReset={this.onFormReset}
                className="pc-final-form flex-rows"
              >
                <PageHeader
                  useBack
                  useSubmit
                  theme="red"
                  title={config.title}
                  isloading={isloading}
                  canSubmit={!pristine && canSubmit}
                />
                <main
                  role="main"
                  className="pc-main is-relative flex-1"
                  style={{ backgroundImage }}
                >
                  <div className="pc-scroll-container">
                    <div className="padded flex-1">
                      <InputField
                        required
                        name={config.key}
                        label={config.label}
                        disabled={isloading}
                        defaultValue={defaultValue}
                      />
                    </div>
                  </div>
                </main>
              </form>
            )
          }}
        />
        <NavigationFooter
          theme="white"
          disabled={isloading}
          className="dotted-top-red"
        />
      </div>
    )
  }
}

ProfileEditForm.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(ProfileEditForm)
