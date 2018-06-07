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
      hasExistingImage: false,
      isEdited: false,
      readOnly: false,
      image: null,
      isUploadDisabled: false,
      isDragging: false,
      zoom: 1,
    }
  }

  static getDerivedStateFromProps(props, prevState) {
    const hasExistingImage = typeof props.image === 'string'
    const readOnly = hasExistingImage && !prevState.isEdited
    return {
      hasExistingImage,
      readOnly,
      image: readOnly ? props.image : prevState.image,
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
      requestData,
      storeKey
    } = this.props
    const {
      image,
      isUploadDisabled,
    } = this.state
    this.setState({
      isEdited: false,
    })
    if (typeof image === 'string') return;
    if (isUploadDisabled) return;
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
    window && window.URL.revokeObjectURL(image.preview)
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
      className
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
      <div className='field'>
        <div className={classnames('upload-thumb', className)}>
          <Dropzone
            className={classnames('dropzone', { 'has-image': Boolean(image), 'no-drag': readOnly})}
            onDragEnter={this.handleDragStart}
            onDragLeave={this.handleDragStop}
            onDrop={this.handleDrop}
            disableClick={Boolean(image || readOnly)}
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
              color={[255, 255, 255, readOnly || !image ? 1 : 0.6]}
              image={image}
              onImageChange={ctx => onImageChange && onImageChange(this.state.image, ctx)}
            />
          </Dropzone>
          <nav className="field ">
            {
              !readOnly && (
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
            {
              isUploadDisabled && (
                <p className='has-text-danger'>
                  {`Votre image trop volumineuse : ${size.toFixed(2)} < ${maxSize}Mo`}
                </p>
              )
            }
            <div className="field is-grouped is-grouped-centered" >
              <div className="control">
                {readOnly && <button onClick={ e => this.setState({isEdited: true})} className='button is-primary'>Modifier l'image</button>}
                {!readOnly && <button onClick={this.onUploadClick} className='button is-primary' disabled={isUploadDisabled}>Enregistrer</button>}
              </div>
              {!readOnly && (
                <div className="control">
                  <button onClick={e => this.setState({image: null})} className='button is-primary is-outlined'>Changer d'image</button>
                </div>
              )}
              {!readOnly && (
                <div className="control">
                  <button onClick={e => this.setState({isEdited: false})} className='button is-primary is-outlined'>Annuler la modification</button>
                </div>
              )}
            </div>
          </nav>
        </div>
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
