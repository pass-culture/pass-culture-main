import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

import { steps, STEP_ID_PROFILE } from '../HomepageBreadcrumb'

import Support from './Support'

const Profile = ({ user }) => {
  return (
    <>
      <h2
        className="h-section-title"
        id={steps[STEP_ID_PROFILE].hash}
      >
        {'Profil et aide'}
      </h2>

      <div className="h-section-row">
        <div className="h-card h-card-secondary-hover">
          <div className="h-card-inner">
            <div className="h-card-header-row">
              <h3 className="h-card-title">
                {'Profil'}
              </h3>
              <Link
                className="tertiary-button"
                to="/profil"
              >
                <Icon svg="ico-outer-pen" />
                {'Modifier'}
              </Link>
            </div>
            <div className="h-card-content">
              <dl className="h-description-list">
                <dt>
                  {'Nom :'}
                </dt>
                <dd>
                  {user.lastName}
                </dd>

                <dt>
                  {'Prénom :'}
                </dt>
                <dd>
                  {user.firstName}
                </dd>

                <dt>
                  {'E-mail : '}
                </dt>
                <dd>
                  {user.email}
                </dd>

                <dt>
                  {'Téléphone : '}
                </dt>
                <dd>
                  {user.phoneNumber}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <Support />
      </div>
    </>
  )
}

Profile.propTypes = {
  user: PropTypes.shape().isRequired,
}

export default Profile
