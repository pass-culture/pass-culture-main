import React from 'react'

import { URL_FOR_MAINTENANCE } from '../utils/config'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class RedirectToMaintenance extends React.PureComponent {
  componentDidMount() {
    window.location.href = URL_FOR_MAINTENANCE
  }

  render() {
    return null
  }
}

export default RedirectToMaintenance
