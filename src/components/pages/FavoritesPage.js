/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { compose } from 'redux'
import { Scrollbars } from 'react-custom-scrollbars'

import {
  withRedirectToSigninWhenNotAuthenticated,
  withRedirectToDiscoveryOrTypeForm,
} from '../hocs'
import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'
import { ROOT_PATH } from '../../utils/config'

const FavoritesPage = () => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
  return (
    <div id="terms-page" className="page is-relative flex-rows">
      <PageHeader theme="red" title="Mes préférés" />
      <main role="main" className="pc-main my12">
        <Scrollbars>
          <div className="padded content" style={{ backgroundImage }} />
        </Scrollbars>
      </main>
      <NavigationFooter theme="white" className="dotted-top-red" />
    </div>
  )
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withRedirectToDiscoveryOrTypeForm
)(FavoritesPage)
