import React, { Component } from 'react'
import { connect } from 'react-redux'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { NEW } from '../../utils/config'

class UploadThumb extends Component {

  constructor() {
    super()
    this.state = {
      apiPath: null,
      image: null,
      zoom: 1,
    }
  }

  handleDrop = dropped => {
    this.setState({ image: dropped[0] })
  }

  onUploadClick = e => {
    const localFormData = new FormData()
    localFormData.append('image', this.state.image)
    e.target.value = localFormData
    this.props.onUploadClick && this.props.onUploadClick(e)
    window && window.URL.revokeObjectURL(this.state.image.preview)
  }

  onZoomChange = e => {
    this.setState({ zoom: parseFloat(e.target.value) })
  }

  render () {
    const {
      border,
      borderRadius,
      height,
      width
    } = this.props
    const {
      image,
      zoom
    } = this.state

    return [
      <Dropzone
        className={`input upload-thumb ${image && 'has-image'}`}
        key={0}
        onDrop={this.handleDrop}
        disableClick={Boolean(image)}
      >
        {
          image
          ? (
            <button
              onClick={ e => this.setState({image: null})}
              className='remove-image'>
              <Icon svg='ico-close-b' alt="Enlever l'image" />
            </button>
          )
          : (
            <p className="drag-n-drop" style={{ borderRadius }}>
              Cliquez ou glissez-déposez pour charger une image
            </p>
          )
        }
        <AvatarEditor
          width={width}
          height={height}
          scale={zoom}
          border={border}
          borderRadius={borderRadius}
          color={[255, 255, 255, image ? 0.6 : 1]}
          image={image}
        />
        {
          image && (
            <input
              className="zoom level-left"
              key={0}
              type="range"
              min="1"
              max="2"
              step="0.01"
              value={zoom}
              onChange={this.onZoomChange}
            />
          )
        }
      </Dropzone>,
      image && (
        <nav className="level is-mobile" key={1}>
          <button
            className='button is-primary'
            onClick={this.onUploadClick}
          >
            Charger la photo
          </button>
        </nav>
      )
    ]
  }
}

UploadThumb.defaultProps = {
  border: 50,
  borderRadius: 250,
  height: 250,
  entityId: NEW,
  width: 250
}

export default connect(
  null,
  { requestData }
)(UploadThumb)
