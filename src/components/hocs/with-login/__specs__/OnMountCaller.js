import PropTypes from 'prop-types'
import { Component } from 'react'

class OnMountCaller extends Component {
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
