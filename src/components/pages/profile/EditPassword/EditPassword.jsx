import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import EditPasswordField from './EditPasswordField/EditPasswordField'

class EditPassword extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      currentPassword: '',
      errors: null,
      isSubmitButtonDisabled: false,
      newConfirmationPassword: '',
      newPassword: '',
    }

    this.currentPasswordInputRef = React.createRef()
    this.newPasswordInputRef = React.createRef()
    this.newConfirmationPasswordInputRef = React.createRef()
  }

  handleCurrentPassword = event => {
    const newValue = event.target.value
    this.setState({ currentPassword: newValue })
  }

  handleNewPassword = event => {
    const newValue = event.target.value
    this.setState({ newPassword: newValue })
  }

  handleNewConfirmationPassword = event => {
    const newValue = event.target.value
    this.setState({ newConfirmationPassword: newValue })
  }

  handleSubmitSuccess = () => {
    const { historyPush, snackbar, pathToProfile } = this.props
    historyPush(pathToProfile)
    snackbar('Ton mot de passe a bien été modifié.', 'success')
  }

  handleSubmitFail = (state, action) => {
    this.setState({
      errors: { ...action.payload.errors },
      isSubmitButtonDisabled: false,
    })

    if (action.payload.errors.oldPassword) {
      this.currentPasswordInputRef.current.focus()
    } else if (action.payload.errors.newPassword) {
      this.newPasswordInputRef.current.focus()
      this.newPasswordInputRef.current.select()
    } else if (action.payload.errors.newConfirmationPassword) {
      this.newConfirmationPasswordInputRef.current.focus()
      this.newConfirmationPasswordInputRef.current.select()
    }
  }

  handleSubmitPassword = event => {
    event.preventDefault()
    const { handleSubmit } = this.props
    const currentPasswordInputValue = this.currentPasswordInputRef.current.value
    const newPasswordInputValue = this.newPasswordInputRef.current.value
    const newConfirmationPasswordInputValue = this.newConfirmationPasswordInputRef.current.value

    if (newPasswordInputValue !== newConfirmationPasswordInputValue) {
      const payload = {
        payload: {
          errors: {
            newConfirmationPassword: ['Les deux mots de passe ne sont pas identiques.'],
          },
        },
      }
      this.handleSubmitFail(this.state, payload)
    } else {
      const passwordToSubmit = {
        newPassword: newPasswordInputValue,
        oldPassword: currentPasswordInputValue,
      }
      handleSubmit(passwordToSubmit, this.handleSubmitFail, this.handleSubmitSuccess)
      this.setState({ isSubmitButtonDisabled: true })
    }
  }

  render() {
    const { pathToProfile } = this.props
    const {
      currentPassword,
      errors,
      isSubmitButtonDisabled,
      newConfirmationPassword,
      newPassword,
    } = this.state

    return (
      <div className="password-container pf-container">
        <HeaderContainer
          backTo={pathToProfile}
          closeTo={null}
          title="Mot de passe"
        />
        <form
          className="pf-form"
          onSubmit={this.handleSubmitPassword}
        >
          <div>
            <EditPasswordField
              errors={errors && errors.oldPassword}
              inputRef={this.currentPasswordInputRef}
              label="Mot de passe actuel"
              onChange={this.handleCurrentPassword}
              value={currentPassword}
            />
            <EditPasswordField
              errors={errors && errors.newPassword}
              inputRef={this.newPasswordInputRef}
              label="Nouveau mot de passe"
              onChange={this.handleNewPassword}
              placeholder="Ex : m02pass!"
              value={newPassword}
            />
            <EditPasswordField
              errors={errors && errors.newConfirmationPassword}
              inputRef={this.newConfirmationPasswordInputRef}
              label="Confirmation nouveau mot de passe"
              onChange={this.handleNewConfirmationPassword}
              placeholder="Ex : m02pass!"
              value={newConfirmationPassword}
            />
          </div>
          <div className="pf-form-submit">
            <input
              className="pf-button-submit"
              disabled={isSubmitButtonDisabled}
              onClick={this.handleSubmitPassword}
              type="submit"
              value="Enregistrer"
            />
          </div>
        </form>
      </div>
    )
  }
}

EditPassword.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  historyPush: PropTypes.func.isRequired,
  pathToProfile: PropTypes.string.isRequired,
  snackbar: PropTypes.func.isRequired,
}

export default EditPassword
