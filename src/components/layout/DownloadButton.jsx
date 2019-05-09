import PropTypes from 'prop-types'
import React, { Component } from 'react'

const fetchAndDownloadFile = async (href, fileType) => {
  const result = await fetch(href, { credentials: 'include' })
  const text = await result.text()
  const blob = new Blob([text], { type: fileType })
  window.location.href = window.URL.createObjectURL(blob)
}

class DownloadButton extends Component {
  onDownloadClick = () => {
    const { fileType, href } = this.props
    fetchAndDownloadFile(href, fileType)
  }

  render() {
    const { children } = this.props
    return (
      <button
        className="button is-primary"
        onClick={this.onDownloadClick}
        type="button">
        {children}
      </button>
    )
  }
}

DownloadButton.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]),
  fileType: PropTypes.string.isRequired,
}

export default DownloadButton
