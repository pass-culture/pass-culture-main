import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../layout/Icon/Icon'

const NotMatch = () => (
  <div className="not-match">
    <Icon svg="404" />
    <div className="nm-title">
      {'Oh non !'}
    </div>
    <div className="nm-subtitle">
      {"Cette page n'existe pas."}
    </div>
    <Link
      className="nm-redirection-link"
      to="/"
    >
      {'Retour'}
    </Link>
  </div>
)

export default NotMatch
