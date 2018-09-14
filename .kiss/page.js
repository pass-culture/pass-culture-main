/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH } from '../../utils/config'
import PageHeader from '../layout/PageHeader'
import PageFooter from '../layout/PageFooter'

const PageSimple = () => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  return (
    <div id="single-page-id" className="page is-relative flex-rows">
      <PageHeader theme="red" title="A Page Title" />
      <main role="main" className="pc-main">
        <Scrollbars>
          <div className="padded" style={{ backgroundImage }} />
        </Scrollbars>
      </main>
      <PageFooter theme="white" className="dotted-top-red" />
    </div>
  )
}

export default PageSimple
