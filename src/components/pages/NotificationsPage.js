/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import {
  selectCurrentUser,
  withRedirectToSigninOrTypeformAfterLogin,
} from '../hocs'
import Loader from '../layout/Loader'
import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'

const NotificationsPage = ({ currentUser }) => {
  const isCurrentUserLoaded = currentUser || typeof currentUser === 'object'
  return (
    <div id="notifications-page" className="page is-relative flex-rows">
      {isCurrentUserLoaded && (
        <React.Fragment>
          <PageHeader theme="red" title="Mes notifications" />
          <main role="main" className="pc-main is-clipped is-relative">
            <div className="pc-scroll-container" />
          </main>
          <NavigationFooter theme="white" className="dotted-top-primary" />
        </React.Fragment>
      )}
      <Loader isLoading={!isCurrentUserLoaded} />
    </div>
  )
}

NotificationsPage.propTypes = {
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.object])
    .isRequired,
}

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state) || false,
})

export default compose(
  withRedirectToSigninOrTypeformAfterLogin,
  connect(mapStateToProps)
)(NotificationsPage)
