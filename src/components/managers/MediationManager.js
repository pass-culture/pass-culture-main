import { Icon } from 'pass-culture-shared'
import get from 'lodash.get'
import React from 'react'
import ReactMarkdown from 'react-markdown'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import MediationItem from '../items/MediationItem'
import mediationsSelector from '../../selectors/mediations'
import offerSelector from '../../selectors/offer'

const mediationExplanation = `
  **L'accroche permet d'afficher votre offre "à la une" de l'app**, et la rend visuellement plus attrayante. C'est une image, une citation, ou une vidéo, intrigante, percutante, séduisante... en un mot : accrocheuse.

  Les accroches font la **spécificité du Pass Culture**. Prenez le temps de les choisir avec soin !
`

const MediationManager = ({ mediations, offer }) => {
  const mediationsLength = get(mediations, 'length')

  return (
    <div className="box content has-text-centered">
      <ReactMarkdown source={mediationExplanation} className="section" />
      <ul className="mediations-list">
        {mediations.map(m => <MediationItem key={m.id} mediation={m} />)}
      </ul>
      <p>
        {offer && (
          <NavLink
            className={`button is-primary ${
              mediationsLength > 0 ? 'is-outlined' : ''
            }`}
            to={`/offres/${get(offer, 'id')}/accroches/nouveau`}>
            <span className="icon">
              <Icon svg={mediationsLength > 0 ? 'ico-stars' : 'ico-stars-w'} />
            </span>
            <span>Ajouter une accroche</span>
          </NavLink>
        )}
      </p>
    </div>
  )
}

export default compose(
  withRouter,
  connect((state, ownProps) => ({
    mediations: mediationsSelector(state, ownProps.match.params.offerId),
    offer: offerSelector(state, ownProps.match.params.offerId),
  }))
)(MediationManager)
