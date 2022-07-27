import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

import Icon from '../../Icon'
/*eslint no-undef: 0*/
import TextInputWithIcon from '../../inputs/TextInputWithIcon/TextInputWithIcon'

export const isNotValid = value => {
  if (!value) {
    return ['Ce champ est obligatoire']
  }

  return null
}

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class PasswordField extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isPasswordHidden: true,
    }
  }

  getErrorMessage = errors => {
    // When the error reason is identified to be invalid password, we override the backend error message
    // Why ? For legacy reasons, we used to display the backend error message but the tight couplage has become an hindrance to us
    if (errors[0].startsWith('Ton mot de passe')) {
      return `Votre mot de passe doit contenir au moins :
      - 12 caractères
      - Un chiffre
      - Une majuscule et une minuscule
      - Un caractère spécial
      `
    }

    return errors[0]
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

  renderPasswordField = ({ input, meta }) => {
    const { isPasswordHidden } = this.state
    const { errors, label, name } = this.props

    return (
      <TextInputWithIcon
        error={
          errors && (meta.touched || meta.modified)
            ? this.getErrorMessage(errors)
            : null
        }
        icon={isPasswordHidden ? 'ico-eye-close' : 'ico-eye-open'}
        iconAlt={
          isPasswordHidden
            ? 'Afficher le mot de passe'
            : 'Cacher le mot de passe'
        }
        label={label}
        name={name}
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
          name={this.props.name}
          validate={isNotValid}
        />
        {this.props.showTooltip && (
          <Icon
            alt="Caractéristiques obligatoires du mot de passe"
            currentitem="false"
            data-place="bottom"
            data-tip={this.renderPasswordTooltip()}
            data-type="info"
            svg="picto-info"
          />
        )}
      </span>
    )
  }
}

PasswordField.defaultProps = {
  errors: null,
  showTooltip: false,
}

PasswordField.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  showTooltip: PropTypes.bool,
}

export default PasswordField
