import React, { createRef, PureComponent } from 'react'
import PropTypes from 'prop-types'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import EditPasswordField from './EditPasswordField/EditPasswordField'

class EditPassword extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      currentPassword: '',
      errors: null,
      isLoading: false,
      newConfirmationPassword: '',
      newPassword: '',
    }

    this.currentPasswordInputRef = createRef()
    this.newPasswordInputRef = createRef()
    this.newConfirmationPasswordInputRef = createRef()
  }

  handleInputChange = event => {
    const inputName = event.target.name
    const newValue = event.target.value
    this.setState({ [inputName]: newValue })
  }

  checkIfFieldIsMissing = () => {
    const { currentPassword, newConfirmationPassword, newPassword } = this.state

    return currentPassword === '' || newConfirmationPassword === '' || newPassword === ''
  }

  handleSubmitSuccess = () => {
    const { historyPush, triggerSuccessSnackbar, pathToProfile } = this.props
    historyPush(pathToProfile)
    triggerSuccessSnackbar('Ton mot de passe a bien été modifié.')
  }

  handleSubmitFail = (state, action) => {
    this.setState({
      errors: { ...action.payload.errors },
      isLoading: false,
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

    const passwordToSubmit = {
      newPassword: newPasswordInputValue,
      newConfirmationPassword: newConfirmationPasswordInputValue,
      oldPassword: currentPasswordInputValue,
    }
    handleSubmit(passwordToSubmit, this.handleSubmitFail, this.handleSubmitSuccess)
    this.setState({ isLoading: true })
  }

  render() {
    const { pathToProfile } = this.props
    const { currentPassword, errors, isLoading, newConfirmationPassword, newPassword } = this.state
    const isMissingField = this.checkIfFieldIsMissing()

    return (
      <div className="password-container pf-container">
        <HeaderContainer
          backTo={pathToProfile}
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
              name="currentPassword"
              onChange={this.handleInputChange}
              value={currentPassword}
            />
            <EditPasswordField
              errors={errors && errors.newPassword}
              inputRef={this.newPasswordInputRef}
              label="Nouveau mot de passe"
              name="newPassword"
              onChange={this.handleInputChange}
              placeholder="Ex : m02pass!"
              value={newPassword}
            />
            <EditPasswordField
              errors={errors && errors.newConfirmationPassword}
              inputRef={this.newConfirmationPasswordInputRef}
              label="Confirmation nouveau mot de passe"
              name="newConfirmationPassword"
              onChange={this.handleInputChange}
              placeholder="Ex : m02pass!"
              value={newConfirmationPassword}
            />
          </div>
          <div className="pf-form-submit">
            <input
              className="pf-button-submit"
              disabled={isLoading || isMissingField}
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
  triggerSuccessSnackbar: PropTypes.func.isRequired,
}

export default EditPassword
