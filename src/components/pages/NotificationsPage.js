/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { withRedirectToSigninWhenNotAuthenticated } from '../hocs'
import Loader from '../layout/Loader'
import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'

const NotificationsPage = ({ user }) => {
  const isloaded = user || typeof user === 'object'
  return (
    <div id="notifications-page" className="page is-relative flex-rows">
      {isloaded && (
        <React.Fragment>
          <PageHeader theme="red" title="Mes notifications" />
          <main role="main" className="pc-main is-clipped is-relative">
            <div className="pc-scroll-container" />
          </main>
          <NavigationFooter theme="white" className="dotted-top-primary" />
        </React.Fragment>
      )}
      <Loader isloading={!isloaded} />
    </div>
  )
}

NotificationsPage.propTypes = {
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]).isRequired,
}

const mapStateToProps = state => {
  const user = state.user || false
  return { user }
}

export default compose(
  withRouter,
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(NotificationsPage)
