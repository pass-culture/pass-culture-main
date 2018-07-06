import get from 'lodash.get'
import React from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import mediationsSelector from '../selectors/mediations'
import { API_URL } from '../utils/config'

const mediationExplanation = `
  **L'accroche permet d'afficher votre offre "à la une" de l'app**, et la rend visuellement plus attrayante. C'est une image, une citation, ou une vidéo, intrigante, percutante, séduisante... en un mot : accrocheuse.

  Les accroches font la **spécificité du Pass Culture**. Prenez le temps de les choisir avec soin !
`

const MediationManager = ({
  mediations,
  routePath
}) => {
  const mediationsLength = get(mediations, 'length')

  return (
    <div className='box content has-text-centered'>
      <ReactMarkdown source={mediationExplanation} className='section' />
      <ul className='mediations-list'>
        {
          mediations.map(m => (
            <li key={m.id}>
              <img
                alt={`accroche-${m.thumbPath}`}
                src={`${API_URL}${m.thumbPath}`} />
            </li>
          ))
        }
      </ul>
      <p>
        <NavLink
          className={`button is-primary ${mediationsLength > 0 ? 'is-outlined' : ''}`}
          to={`${routePath}/accroches/nouveau`}>
          <span className='icon'><Icon svg={mediationsLength > 0 ? 'ico-stars' : 'ico-stars-w'} /></span>
          <span>Ajouter une accroche</span>
        </NavLink>
      </p>
    </div>
  )
}

export default connect(
  (state, ownProps) => {
    const {eventId, thingId} = ownProps.occasion
    return {
      mediations: mediationsSelector(state, eventId, thingId)
    }
  }
)(MediationManager)
