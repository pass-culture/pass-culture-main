import React from 'react'

import { steps, STEP_ID_PROFILE } from './HomepageBreadcrumb'

const Profile = () => {
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
            <h3 className="h-card-title">
              {'Profil'}
            </h3>
            <div className="h-card-content">
              {'Hello world !'}
            </div>
          </div>
        </div>

        <div className="h-card h-card-secondary-hover">
          <div className="h-card-inner">
            <h3 className="h-card-title">
              {'Aide et support'}
            </h3>
            <div className="h-card-content">
              {'Hello world !'}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Profile
