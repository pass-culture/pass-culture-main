import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component, PureComponent } from 'react'
import { Field } from 'react-final-form'
import Icon from '../../Icon'

class PasswordInput extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isPasswordHidden: true,
    }
  }

  toggleHidden = e => {
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

  render() {
    const { isPasswordHidden } = this.state

    return (
      <span className="field-password">
        <Field
          {...this.props}
          component='input'
          type={isPasswordHidden ? 'password' : 'text'}
        />
        <button
          className="button button-show-password"
          onClick={this.toggleHidden}
          type="button"
        >
          <Icon
            alt={isPasswordHidden ? 'Afficher le mot de passe' : 'Cacher le mot de passe'}
            svg={isPasswordHidden ? 'ico-eye close' : 'ico-eye'}
          />
            &nbsp;
        </button>

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

export default PasswordInput
