import React from 'react'
import { Scrollbars } from 'react-custom-scrollbars'

import { withRequiredLogin } from '../hocs'
import PageHeader from '../layout/Header/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'
import { ROOT_PATH } from '../../utils/config'

const FavoritesPage = () => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
  return (
    <div
      className="page is-relative flex-rows"
      id="terms-page"
    >
      <PageHeader title="Mes préférés" />
      <main
        className="pc-main my12"
        role="main"
      >
        <Scrollbars>
          <div
            className="padded content"
            style={{ backgroundImage }}
          />
        </Scrollbars>
      </main>
      <NavigationFooter
        className="dotted-top-red"
        theme="white"
      />
    </div>
  )
}

export default withRequiredLogin(FavoritesPage)
