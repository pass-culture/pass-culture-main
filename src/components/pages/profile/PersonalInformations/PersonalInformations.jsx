import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import { MesInformationsField } from '../forms/fields/MesInformationsField'
import HeaderContainer from '../../../layout/Header/HeaderContainer'

class PersonalInformations extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      publicName: props.user.publicName,
      errors: null,
    }

    this.publicNameInputRef = React.createRef()
  }

  handlePublicNameChange = event => {
    const newValue = event.target.value
    this.setState({ publicName: newValue })
  }

  handleSubmitFail = (state, action) => {
    this.setState({ errors: { ...action.payload.errors } })
    this.publicNameInputRef.current.focus()
    this.publicNameInputRef.current.select()
  }

  handleSubmitSuccess = () => {
    const { history, displaySnackbar, pathToProfile } = this.props
    this.setState({ errors: null })
    history.push(pathToProfile)
    displaySnackbar('Ton pseudo a bien été modifié.', 'success')
  }

  handleSubmitPublicName = () => {
    const { handleSubmit, user, pathToProfile, history } = this.props
    const publicNameInputValue = this.publicNameInputRef.current.value
    const publicNameToSubmit = {
      publicName: publicNameInputValue,
    }

    if (user.publicName !== publicNameInputValue) {
      handleSubmit(publicNameToSubmit, this.handleSubmitFail, this.handleSubmitSuccess)
    } else {
      history.push(pathToProfile)
    }
  }

  render() {
    const { user, getDepartment } = this.props
    const { errors, publicName } = this.state
    return (
      <div className="pi-container">
        <HeaderContainer
          backTo="/profil"
          closeTo={null}
          title="Informations personnelles"
        />
        <form className="pi-form">
          <MesInformationsField
            errors={errors && errors.publicName}
            id="identifiant"
            label="Pseudo"
            maxLength={255}
            minLength={3}
            name="publicName"
            onChange={this.handlePublicNameChange}
            ref={this.publicNameInputRef}
            required
            value={publicName}
          />
          <MesInformationsField
            disabled
            id="name"
            label="Nom et prénom"
            name="name"
            value={`${user.firstName} ${user.lastName}`}
          />
          <MesInformationsField
            disabled
            id="email"
            label="Adresse e-mail"
            name="email"
            value={user.email}
          />
          <MesInformationsField
            disabled
            id="departementCode"
            label="Département de résidence"
            name="departementCode"
            value={getDepartment(user.departementCode)}
          />
        </form>
        <div className="pi-form-submit">
          <button
            className="button-submit"
            onClick={this.handleSubmitPublicName}
            type="button"
          >
            {'Enregistrer'}
          </button>
        </div>
      </div>
    )
  }
}

PersonalInformations.propTypes = {
  displaySnackbar: PropTypes.func.isRequired,
  getDepartment: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  pathToProfile: PropTypes.string.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default PersonalInformations
