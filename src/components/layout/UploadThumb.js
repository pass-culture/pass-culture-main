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
      isEdited: false,
      readOnly: false,
      image: null,
      isUploadDisabled: false,
      isDragging: false,
      zoom: 1,
    }
  }

  static getDerivedStateFromProps(props, prevState) {
    return {
      readOnly: prevState.isEdited ? prevState.readOnly : Boolean(props.image),
      image: prevState.isEdited ? prevState.image : props.image,
    }
    return prevState;
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
    this.setState({
      readOnly: true,
    })
    if (typeof image === 'string') return;
    e.preventDefault()
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
      width,
      onImageChange,
    } = this.props
    const {
      image,
      dragging,
      isUploadDisabled,
      readOnly,
      size,
      zoom
    } = this.state

    return (
      <div className='upload-thumb'>
        <div className='field'>
          <div className={this.props.className}>
          {image && (
            <ul className='actions'>
              {readOnly ? (
                <li>
                  <button
                    onClick={ e => this.setState({readOnly: false, isEdited: true})}>
                    <Icon svg='ico-pen' alt="Modifier l'image" />
                  </button>
                </li>
              ) : (
                <li>
                  <button
                    onClick={ e => this.setState({image: null, readOnly: false})}>
                    <Icon svg='ico-close-b' alt="Enlever l'image" />
                  </button>
                </li>
              )}
            </ul>
          )}
          { readOnly ? (
            <img style={{borderRadius, width, height, borderWidth: border}} src={this.props.image} className='read-only' />
            ) : (
              <Dropzone
                className={`dropzone ${image && 'has-image'}`}
                onDragEnter={this.handleDragStart}
                onDragLeave={this.handleDragStop}
                onDrop={this.handleDrop}
                disableClick={Boolean(image)}
              >
                {
                  !image && (
                    <div className={`drag-n-drop ${dragging ? 'dragged' : ''}`} style={{ borderRadius, width, height }}>
                      Cliquez ou glissez-déposez pour charger une image
                    </div>
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
                  onImageChange={ctx => onImageChange && onImageChange(this.state.image, ctx)}
                />
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
            )
          }
        </div>
        </div>
        <nav className="field ">
          {
            isUploadDisabled && (
              <p>
                {`(Image trop grosse ${size.toFixed(2)} < ${maxSize}MB)`}
              </p>
            )
          }
          {!this.state.readOnly && (

            <div className="field is-grouped is-grouped-centered" style={{justifyContent: 'space-between'}}>
              <div className="control">
                <button onClick={this.onUploadClick} className='button is-primary'>Enregistrer</button>
              </div>
              <div className="control">
                <button onClick={e => this.setState({readOnly: true})} className='button is-primary is-outlined'>Annuler</button>
              </div>
            </div>
          )}
        </nav>
      </div>
    )
  }
}

UploadThumb.defaultProps = {
  border: 25,
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
