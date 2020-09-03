import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'
import Icon from '../../Icon'
import TextInputWithIcon from '../../inputs/TextInputWithIcon/TextInputWithIcon'
import PropTypes from 'prop-types'

export const isNotValid = value => {
  return !value
}

class PasswordField extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isPasswordHidden: true,
    }
  }

  handleToggleHidden = e => {
    e.preventDefault()
    this.setState(previousState => ({
      isPasswordHidden: !previousState.isPasswordHidden,
    }))
  }

  renderPasswordTooltip = () => {
    return `
          <Fragment>Votre mot de passe doit contenir au moins :
            <ul>
              <li>12 caractères</li>
              <li>une majuscule et une minuscule</li>
              <li>un chiffre</li>
              <li>un caractère spécial (signe de ponctuation, symbole monétaire ou mathématique)</li>
            </ul>
          </Fragment>`
  }

  renderPasswordField = ({ input }) => {
    const { isPasswordHidden } = this.state
    const { errors } = this.props

    return (
      <TextInputWithIcon
        error={errors ? errors[0] : null}
        icon={isPasswordHidden ? 'ico-eye-close' : 'ico-eye-open'}
        iconAlt={isPasswordHidden ? 'Afficher le mot de passe' : 'Cacher le mot de passe'}
        label="Mot de passe"
        name="password"
        onChange={input.onChange}
        onIconClick={this.handleToggleHidden}
        placeholder="Mon mot de passe"
        type={isPasswordHidden ? 'password' : 'text'}
        value={input.value}
      />
    )
  }

  render() {
    return (
      <span className="field-password">
        <Field
          component={this.renderPasswordField}
          name="password"
          validate={isNotValid}
        />
        <Icon
          alt="Caractéristiques obligatoires du mot de passe"
          currentitem="false"
          data-place="bottom"
          data-tip={this.renderPasswordTooltip()}
          data-type="info"
          svg="picto-info"
        />
      </span>
    )
  }
}

PasswordField.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export default PasswordField
