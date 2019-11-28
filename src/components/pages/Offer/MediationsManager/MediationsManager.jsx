import { Icon } from 'pass-culture-shared'
import get from 'lodash.get'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'

import MediationItem from './MediationItem/MediationItem'
import PropTypes from 'prop-types'

export const NO_MEDIATION_TOOLTIP =
  '<div><p>Pour que votre offre soit mise en avant dans l’application du pass Culture, vous devez&nbsp;:</p>' +
  '<p>- ajouter une ou plusieurs accroches</p>' +
  '<p>- sélectionner au moins une accroche</p></div>'


class MediationsManager extends PureComponent {
  componentDidMount() {
    const { showNotification, hasMediations, atLeastOneActiveMediation, notification } = this.props

    if (!notification && !(hasMediations && atLeastOneActiveMediation)) {
      showNotification({
        tag: 'mediations-manager',
        text:
          'Cette offre ne sera pas mise en avant dans l’application pass Culture mais sera accessible via la recherche par mots-clés.',
        tooltip: {
          children:
  <span>
    {'Pourquoi ?'}
  </span>,
          place: 'bottom',
          tip: NO_MEDIATION_TOOLTIP,
          type: 'info',
        },
        type: 'warning',
      })
    }
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (get(notification, 'tag') === 'mediations-manager') {
      closeNotification()
    }
  }

  render() {
    const { mediations, offer } = this.props
    const numberOfMediations = get(mediations, 'length')

    return (
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
    )
  }
}

MediationsManager.defaultProps = {
  notification: null,
}

MediationsManager.propTypes = {
  mediations: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  notification: PropTypes.shape(),
  offer: PropTypes.shape({
    id: PropTypes.string,
  }).isRequired,
}

export default MediationsManager
