import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'

// import FormInput from './layout/FormInput'
import SwitchButton from './layout/SwitchButton'
import { requestData } from '../reducers/data'
import selectOccasionThumbUrl from '../selectors/occasionThumbUrl'
import { collectionToPath } from '../utils/translate'

class OccasionItem extends Component {
  onDeactivateClick = event => {
    const {
      id,
      occasionType,
      requestData
    } = this.props
    requestData(
      'PATCH',
      `occasions/${occasionType}/${id}`,
        {
          body: {
            occasion: {
              isActive: event.target.value
            }
          },
          key: 'occasions',
          isMergingDatum: true,
          isMutatingDatum: true,
          isMutaginArray: false
        }
      )
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
              <NavLink  to={`/offres/${collectionToPath(occasionType)}/${id}/accroches`}>
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
              {/*
              <FormInput
                collectionName={occasionType}
                defaultValue={isActive}
                entityId={id}
                name='isActive'

                type='switch'
              />
              */}
              <SwitchButton
                isInitialActive={isActive}
                OffElement={<p> Désactivé </p>}
                OnElement={<p> Activé </p>}
                onClick={this.onDeactivateClick}
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



export default connect(
  () => {
    return (state, ownProps) => ({
      thumbUrl: selectOccasionThumbUrl(state, ownProps)
    })
  },
  { requestData }
)(OccasionItem)
