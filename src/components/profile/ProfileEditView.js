/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'pass-culture-shared'
import { bindActionCreators, compose } from 'redux'
import { Form as FinalForm } from 'react-final-form'

import { ROOT_PATH } from '../../utils/config'
import { InputField } from '../forms/inputs'
import PageHeader from '../layout/PageHeader'
import FormControls from '../forms/FormControls'
import NavigationFooter from '../layout/NavigationFooter'

class ProfileEditView extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch, user } = this.props
    // initialValues sont detruites a chaque mount/unmount
    this.initialValues = Object.assign({}, user)
    this.state = { hasfailed: false, isloading: false }
    this.actions = bindActionCreators({ requestData }, dispatch)
  }

  handleRequestFail = () => {
    const nextstate = { hasfailed: true, isloading: false }
    this.setState(nextstate)
  }

  handleRequestSuccess = () => {
    const { history, location } = this.props
    const nextlocation = `${location.pathname}/success`
    const nextstate = { hasfailed: false, isloading: false }
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
    // reset des donnees en BDD uniquement si les valeurs ont changees
    // const shouldreset = !isEqual(user, this.initialValues)
    // if (!shouldreset) return history.goBack()
    // return this.onFormSubmit(this.initialValues, () => {})
  }

  renderInputByView = () => {}

  render() {
    const { isloading, hasfailed } = this.state
    const { match } = this.props
    const { view } = match.params
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    const defaultValue = this.initialValues[view]
    const formdisabled = isloading || hasfailed
    return (
      <div
        id="profile-page-edit-view"
        className="pc-page-view transition-item pc-theme-default flex-rows"
      >
        <PageHeader
          theme="red"
          canBack={!isloading}
          title="Editer Mon profil"
        />
        <main
          role="main"
          className="pc-main is-relative flex-1"
          style={{ backgroundImage }}
        >
          <FinalForm
            onSubmit={this.onFormSubmit}
            initialValues={this.initialValues || {}}
            render={({ handleSubmit, invalid, pristine }) => {
              const canSubmit = !pristine || !invalid
              return (
                <form
                  onSubmit={handleSubmit}
                  onReset={this.onFormReset}
                  className="pc-form flex-rows"
                >
                  <div className="padded-2x flex-1">
                    <InputField
                      name={view}
                      label="Field label"
                      disabled={formdisabled}
                      defaultValue={defaultValue}
                    />
                  </div>
                  <FormControls
                    canCancel
                    isLoading={isloading}
                    canSubmit={canSubmit}
                    submitLabel="Modifier"
                  />
                </form>
              )
            }}
          />
        </main>
        <NavigationFooter theme="red" />
      </div>
    )
  }
}

ProfileEditView.propTypes = {
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
)(ProfileEditView)
