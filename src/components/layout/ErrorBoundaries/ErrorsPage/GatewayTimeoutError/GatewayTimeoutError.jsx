import React from 'react'

import { ICONS_URL } from '../../../../../utils/config'

const GatewayTimeoutError = () => (
  <main className="ep-wrapper">
    <img
      alt=""
      src={`${ICONS_URL}/ico-people.svg`}
    />
    <h1>
      {'Il y a foule !'}
    </h1>
    <div className="ep-text-wrapper">
      <div>
        {'Vous êtes très nombreux à vouloir'}
      </div>
      <div>
        {'accéder cette page.'}
      </div>
      <div>
        {'Reviens un peu plus tard.'}
      </div>
    </div>
  </main>
)

export default GatewayTimeoutError
