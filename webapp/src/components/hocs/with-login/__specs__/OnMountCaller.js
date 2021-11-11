import PropTypes from 'prop-types'
import { PureComponent } from 'react'

class OnMountCaller extends PureComponent {
  componentDidMount() {
    const { onMountCallback } = this.props
    onMountCallback()
  }

  render() {
    return null
  }
}

OnMountCaller.defaultProps = {
  onMountCallback: () => {},
}

OnMountCaller.propTypes = {
  onMountCallback: PropTypes.func,
}

export default OnMountCaller
