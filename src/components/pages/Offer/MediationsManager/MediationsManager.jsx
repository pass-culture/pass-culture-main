import { Icon } from 'pass-culture-shared'
import get from 'lodash.get'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'

import MediationItem from './MediationItem/MediationItem'
import PropTypes from 'prop-types'

class MediationsManager extends PureComponent {
  hasNoActiveMediation() {
    const { hasMediations, atLeastOneActiveMediation } = this.props
    return !(hasMediations && atLeastOneActiveMediation)
  }

  render() {
    const { mediations, offer } = this.props
    const numberOfMediations = get(mediations, 'length')

    return (
      <div className="mediation-manager">
        {this.hasNoActiveMediation() && (
          <p className="info-message">
            {"Ajoutez une accroche pour mettre cette offre en avant dans l'application"}
          </p>
        )}

        <div className="box content has-text-centered">
          <div className="section small-text align-left">
            <p>
              <b>
                {'L’accroche permet d’afficher votre offre "à la une" de l’app'}
              </b>
              {', et la rend visuellement plus attrayante. C’est une image (et bientôt '}
              {
                'une phrase ou une vidéo) intrigante, percutante, séduisante... en un mot : accrocheuse.'
              }
            </p>
            <p>
              {'Les accroches font la '}
              <b>
                {'spécificité du pass Culture'}
              </b>
              {'. Prenez le'}
              {'temps de les choisir avec soin !'}
            </p>
          </div>
          <ul className="mediations-list">
            {mediations.map(m => (
              <MediationItem
                key={m.id}
                mediation={m}
              />
            ))}
          </ul>
          <p>
            {offer && (
              <NavLink
                className={`button is-primary ${numberOfMediations > 0 ? 'is-outlined' : ''}`}
                to={`/offres/${get(offer, 'id')}/accroches/nouveau`}
              >
                <span className="icon">
                  <Icon svg={numberOfMediations > 0 ? 'ico-stars' : 'ico-stars-w'} />
                </span>
                <span>
                  {'Ajouter une accroche'}
                </span>
              </NavLink>
            )}
          </p>
        </div>
      </div>
    )
  }
}

MediationsManager.propTypes = {
  mediations: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  offer: PropTypes.shape({
    id: PropTypes.string,
  }).isRequired,
}

export default MediationsManager
