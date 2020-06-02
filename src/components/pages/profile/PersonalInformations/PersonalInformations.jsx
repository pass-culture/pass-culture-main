import React, { createRef, PureComponent } from 'react'
import PropTypes from 'prop-types'

import PersonalInformationsField from './PersonalInformationsField/PersonalInformationsField'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import User from '../ValueObjects/User'

class PersonalInformations extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      errors: null,
      isSubmitButtonDisabled: false,
      nickname: props.user.publicName,
    }

    this.nicknameInputRef = createRef()
  }

  handleNicknameChange = event => {
    const newValue = event.target.value
    this.setState({ nickname: newValue })
  }

  handleSubmitFail = (state, action) => {
    this.setState({
      errors: { ...action.payload.errors },
      isSubmitButtonDisabled: false,
    })
    this.nicknameInputRef.current.focus()
    this.nicknameInputRef.current.select()
  }

  handleSubmitSuccess = () => {
    const { historyPush, triggerSuccessSnackbar, pathToProfile } = this.props
    historyPush(pathToProfile)
    triggerSuccessSnackbar('Ton pseudo a bien été modifié.')
  }

  handleSubmitNickname = event => {
    event.preventDefault()
    const { handleSubmit, historyPush, user, pathToProfile } = this.props
    const { isSubmitButtonDisabled } = this.state
    const nicknameInputValue = this.nicknameInputRef.current.value
    const nicknameToSubmit = {
      publicName: nicknameInputValue,
    }

    if (user.publicName !== nicknameInputValue && !isSubmitButtonDisabled) {
      this.setState({ isSubmitButtonDisabled: true })
      handleSubmit(nicknameToSubmit, this.handleSubmitFail, this.handleSubmitSuccess)
    } else {
      historyPush(pathToProfile)
    }
  }

  render() {
    const { user, department, pathToProfile } = this.props
    const { errors, isSubmitButtonDisabled, nickname } = this.state

    return (
      <div className="pf-container">
        <HeaderContainer
          backTo={pathToProfile}
          closeTo={null}
          title="Informations personnelles"
        />
        <form
          className="pf-form"
          onSubmit={this.handleSubmitNickname}
        >
          <div>
            <PersonalInformationsField
              errors={errors && errors.publicName}
              label="Pseudo"
              maxLength={255}
              minLength={3}
              name="publicName"
              onChange={this.handleNicknameChange}
              ref={this.nicknameInputRef}
              required
              value={nickname}
            />
            <PersonalInformationsField
              disabled
              label="Nom et prénom"
              name="name"
              value={`${user.firstName} ${user.lastName}`}
            />
            <PersonalInformationsField
              disabled
              label="Adresse e-mail"
              name="email"
              value={user.email}
            />
            <PersonalInformationsField
              disabled
              label="Département de résidence"
              name="departementCode"
              value={department}
            />
          </div>
          <div className="pf-form-submit">
            <input
              className="pf-button-submit"
              disabled={isSubmitButtonDisabled}
              onClick={this.handleSubmitNickname}
              type="submit"
              value="Enregistrer"
            />
          </div>
        </form>
      </div>
    )
  }
}

PersonalInformations.propTypes = {
  department: PropTypes.string.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  historyPush: PropTypes.func.isRequired,
  pathToProfile: PropTypes.string.isRequired,
  triggerSuccessSnackbar: PropTypes.func.isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default PersonalInformations
