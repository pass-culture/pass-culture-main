import React from 'react'
import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'

import { version } from '../../../../package.json'

const EMPTY_FIELD_PLACEHOLDER = 'Non renseigné'

class MesInformations extends React.PureComponent {
  renderInformation = field => {
    const { user } = this.props
    const { key, label, mainPlaceholder, resolver, routeName } = field
    const disabled = !field.component
    // NOTE: par défaut on sette la valeur sur la clé de l'objet user
    // pour le password on ne souhaite pas affiché la valeur
    // pour cela on utilise le resolver retournant une valeur falsey
    const value = (resolver && resolver(user, key)) || user[key]
    return (
      <div
        className="item dotted-bottom-black"
        key={key}
      >
        <NavLink
          className="pc-text-button text-left no-decoration flex-columns items-center pt20 pb22"
          to={disabled ? '#' : `/profil/${routeName}`}
        >
          <span className="is-block flex-1">
            <span className="pc-label pb3 is-block is-grey-text is-uppercase fs13 is-medium">
              {label}
            </span>
            {value && <span className="is-block is-black-text fs18 is-bold">{value}</span>}
            {!value && (
              <span className="is-block is-grey-text fs18">
                {mainPlaceholder || EMPTY_FIELD_PLACEHOLDER}
              </span>
            )}
          </span>
          {!disabled && (
            <span className="is-block flex-0">
              <span
                aria-hidden
                className="icon-legacy-next"
                title={`Modifier ${label}`}
              />
            </span>
          )}
        </NavLink>
      </div>
    )
  }

  render() {
    const { fields } = this.props
    return (
      <div
        className="pb40 pt20"
        id="mes-informations"
      >
        <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb6 px12 fs15 is-italic fs15 is-normal">
          {'Mes Informations'}
        </h3>
        <div className="px12 pc-list">{fields.map(this.renderInformation)}</div>
        <div className="app-version">{`v${version}`}</div>
      </div>
    )
  }
}

MesInformations.propTypes = {
  fields: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default MesInformations
