import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

import getDepartementByCode from '../../../../utils/getDepartementByCode'
import { MesInformationsField } from '../forms/fields/MesInformationsField'

class MesInformations extends PureComponent {
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

  handleBlur = event => {
    const { handleSubmit } = this.props
    const formValuesByNames = Array.from(event.target.form)
      .filter(input => !input.disabled)
      .reduce((fields, input) => {
        fields[input.name] = input.value
        return fields
      }, {})

    handleSubmit(formValuesByNames, this.handleSubmitFail, this.handleSubmitSuccess)
  }

  handleSubmitFail = (state, action) => {
    this.setState({ errors: { ...action.payload.errors } })
    this.publicNameInputRef.current.focus()
  }

  handleSubmitSuccess = () => {
    this.setState({ errors: null })
  }

  getDepartment(departmentCode) {
    const departmentName = getDepartementByCode(departmentCode)
    return `${departmentName} (${departmentCode})`
  }

  render() {
    const { user } = this.props
    const { errors, publicName } = this.state
    return (
      <Fragment>
        <div className="mes-informations-title-container">
          <h2 className="mes-informations-title">
            {'Mes informations'}
          </h2>
        </div>
        <form>
          <MesInformationsField
            errors={errors && errors.publicName}
            id="identifiant"
            label="Identifiant"
            name="publicName"
            onBlur={this.handleBlur}
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
            id="departmentCode"
            label="Département de résidence"
            name="departementCode"
            value={this.getDepartment(user.departementCode)}
          />
        </form>
        <div className="mi-change-password">
          <label>
            {'Mot de passe'}
          </label>
          <Link to="/profil/password">
            {'Changer mon mot de passe'}
          </Link>
        </div>
      </Fragment>
    )
  }
}

MesInformations.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default MesInformations
