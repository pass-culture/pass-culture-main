import { PureComponent } from 'react'
import { URL_FOR_MAINTENANCE } from '../utils/config'

class RedirectToMaintenance extends PureComponent {
  componentDidMount() {
    window.location.href = URL_FOR_MAINTENANCE
  }

  render() {
    return null
  }
}

export default RedirectToMaintenance
