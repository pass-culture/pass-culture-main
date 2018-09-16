/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { withLogin } from 'pass-culture-shared'
import { Scrollbars } from 'react-custom-scrollbars'

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
          <main role="main" className="is-relative flex-1">
            <Scrollbars autoHide />
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
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(NotificationsPage)
