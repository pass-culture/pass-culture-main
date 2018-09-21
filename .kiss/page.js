/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

import { ROOT_PATH } from '../../utils/config'
import PageHeader from '../layout/PageHeader'
import PageFooter from '../layout/PageFooter'

const PageSimple = () => {
  const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
  return (
    <div id="single-page-id" className="page is-relative flex-rows">
      <PageHeader theme="red" title="A Page Title" />
      <main role="main" className="pc-main is-clipped is-relative">
        <div className="pc-scroll-container">
          <div className="padded" style={{ backgroundImage }} />
        </div>
      </main>
      <PageFooter theme="white" className="dotted-top-red" />
    </div>
  )
}

export default PageSimple
