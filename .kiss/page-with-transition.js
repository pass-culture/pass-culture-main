/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import PageTransition from 'react-router-page-transition'
import { Route, Switch, withRouter } from 'react-router-dom'

const PageWithTransition = ({ location }) => {
  return (
    <div id="page-with-transition-id" className="page is-relative">
      <PageTransition timeout={500}>
        <Switch location={location}>
          <Route
            exact
            path="/main-route"
            // component={ProfileMainView}
            key="route-profile-main-view"
            render={() => (
              <div
                id="main-view-id"
                className="pc-page-view-main transition-item">
                <span>
                  Render is used only for demo, use component prop instead
                </span>
              </div>
            )}
          />
          <Route
            exact
            path="/main-route/:route-parameter"
            // component={ProfileMainView}
            key="route-profile-sub-view"
            render={() => (
              <div id="sub-view-id" className="pc-page-view transition-item" />
            )}
          />
        </Switch>
      </PageTransition>
    </div>
  )
}

PageWithTransition.propTypes = {
  location: PropTypes.object.isRequired,
}

export default PageWithTransition
