import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import FormInput from './layout/FormInput'
import selectOccasionThumbUrl from '../selectors/occasionThumbUrl'
import { collectionToPath } from '../utils/translate'

class OccasionItem extends Component {
  onDeactivateClick = () => {

  }

  render() {
    const {
      description,
      id,
      isActive,
      name,
      occasionType,
      thumbUrl
    } = this.props
    return (
      <article className="occasion-item media">
        <figure className="media-left">
          <p className="image is-96x96 is-2by3">
            <img alt='thumbnail' src={thumbUrl}/>
          </p>
        </figure>
        <div className="media-content">
          <div className="content">
            <NavLink className='title is-block' to={`/offres/${collectionToPath(occasionType)}/${id}`}>
              {name}
            </NavLink>
            <Dotdotdot className='is-small' clamp={3}>
              {description}
            </Dotdotdot>
          </div>
          <nav className="level is-mobile">
            <div className="level-left">
              <NavLink  to={`/offres/${collectionToPath(occasionType)}/${id}`}>
                <button className="button is-primary level-item">
                  Modifier
                </button>
              </NavLink>
              <NavLink  to={`/offres/${collectionToPath(occasionType)}/${id}`}>
                <button className="button is-primary level-item">
                  Accroches
                </button>
              </NavLink>
              {/*
              <button className="button is-primary level-item"
                onClick={this.onDeactivateClick}>
                Désactiver
              </button>
              */}

              <FormInput
                collectionName={occasionType}
                defaultValue={isActive}
                entityId={id}
                name='isActive'
                OffElement={<p> Désactivé </p>}
                OnElement={<p> Activé </p>}
                type='switch'
              />
            </div>
          </nav>
        </div>
      </article>
    )
  }
}

OccasionItem.defaultProps = {
  maxDescriptionLength: 300,
}



export default compose(
  withRouter,
  connect(
    () => {
      return (state, ownProps) => ({
        thumbUrl: selectOccasionThumbUrl(state, ownProps)
      })
    }
  )
)(OccasionItem)
