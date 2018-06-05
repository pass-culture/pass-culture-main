import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import get from 'lodash.get'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { API_URL, NEW } from '../../utils/config'

class UploadThumb extends Component {

  constructor() {
    super()
    this.state = {
      apiPath: null,
      image: null,
      isUploadDisabled: false,
      isDragging: false,
      zoom: 1,
    }
    this.$avatarComponent = React.createRef()
  }

  static getDerivedStateFromProps(props) {
    return {
      image: props.image,
    }
  }

  handleDragStart = e => {
    this.setState({
      dragging: true,
    })
  }

  handleDragStop = e => {
    this.setState({
      dragging: false,
    })
  }

  handleDrop = dropped => {
    const image = dropped[0]
    // convert into MB
    const size = image.size/1048576
    this.setState({
      isDragging: false,
      isUploadDisabled: size > this.props.maxSize,
      image,
      size,
    })
  }

  onUploadClick = e => {
    const {
      collectionName,
      entityId,
      index,
      onUploadClick,
      requestData,
      storeKey
    } = this.props
    const { image } = this.state
    if (onUploadClick) {
      e.target.value = image
      this.props.onUploadClick(e)
    } else {
      e.preventDefault()
      console.log(image)
      const type = image.type.includes('image/') && image.type.split('image/')[1]
      const formData = new FormData();
      formData.append('file', image);
      requestData(
        'POST',
        `storage/thumb/${collectionName}/${entityId}/${index}`,
        {
          body: formData,
          encode: 'multipart/form-data',
          key: storeKey
        }
      )
    }
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
      maxSize,
      width
    } = this.props
    const {
      dragging,
      image,
      isUploadDisabled,
      size,
      zoom
    } = this.state

    return [
      <div className='field' key={0}>
        <Dropzone
          className={`input upload-thumb ${image && 'has-image'}`}
          onDragEnter={this.handleDragStart}
          onDragLeave={this.handleDragStop}
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
              <div className={`drag-n-drop ${dragging ? 'dragged' : ''}`} style={{ borderRadius, margin: `${this.props.border}px` }}>
                Cliquez ou glissez-déposez pour charger une image
              </div>
            )
          }
          <div className='avatar-wrapper'>
            <AvatarEditor
              ref={this.$avatarComponent}
              width={width}
              height={height}
              scale={zoom}
              border={border}
              borderRadius={borderRadius}
              color={[255, 255, 255, image ? 0.6 : 1]}
              image={image}
            />
          </div>
          {
            image && (
              <input
                className="zoom level-left"
                key={0}
                type="range"
                min="1"
                max="3"
                step="0.01"
                value={zoom}
                onChange={this.onZoomChange}
              />
            )
          }
        </Dropzone>
      </div>,
      image && (
        <nav className="field " key={1}>
          <button
            className={classnames('button is-primary', {
              disabled: isUploadDisabled
            })}
            disabled={isUploadDisabled}
            onClick={this.onUploadClick}
          >
            Charger
          </button>
          {
            isUploadDisabled && (
              <p>
                {`(Image trop grosse ${size.toFixed(2)} < ${maxSize}MB)`}
              </p>
            )
          }
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
  index: 0,
  maxSize: 2, // in MB
  width: 250
}

export default connect(
  null,
  { requestData }
)(UploadThumb)
