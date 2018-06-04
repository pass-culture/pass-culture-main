import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'

import Icon from './Icon'
import { requestData } from '../../reducers/data'
import { API_URL, NEW } from '../../utils/config'

function formatBytes(a,b){if(0==a)return"0 Bytes";var c=1024,d=b||2,e=["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"],f=Math.floor(Math.log(a)/Math.log(c));return parseFloat((a/Math.pow(c,f)).toFixed(d))+" "+e[f]}

class UploadThumb extends Component {

  constructor() {
    super()
    this.state = {
      apiPath: null,
      image: null,
      isUploadDisabled: false,
      zoom: 1,
    }
  }

  handleDrop = dropped => {
    const image = dropped[0]
    const size = image.size/1048576
    console.log('size', image.size, (image.size/1048576).toFixed(2))
    this.setState({
      image,
      isUploadDisabled: size > this.props.maxSize,
      size
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
      image,
      isUploadDisabled,
      size,
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
