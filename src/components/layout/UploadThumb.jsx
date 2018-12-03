import classnames from 'classnames'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import { connect } from 'react-redux'

class UploadThumb extends Component {
  constructor() {
    super()
    this.avatarEditor = React.createRef()
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
    // const hasExistingImage = typeof props.image === 'string'
    const readOnly = props.hasExistingImage && !prevState.isEdited
    return {
      readOnly,
      isDragging: prevState.isDragging,
      image: props.image || prevState.image,
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
    const size = image.size / 1048576
    this.setState({
      isDragging: false,
      isUploadDisabled: size > this.props.maxSize,
      image,
      size,
    })
  }

  onUploadClick = e => {
    const { collectionName, dispatch, entityId, index, storeKey } = this.props
    const { image, isUploadDisabled } = this.state
    this.setState({
      isEdited: false,
    })
    if (typeof image === 'string') return
    if (isUploadDisabled) return
    e.preventDefault()
    // const type = image.type.includes('image/') && image.type.split('image/')[1]
    const formData = new FormData()
    formData.append('file', image)
    if (!entityId) {
      console.warn('entityId not defined for upload')
    }
    dispatch(
      requestData(
        'POST',
        `storage/thumb/${collectionName}/${entityId}/${index}`,
        {
          body: formData,
          encode: 'multipart/form-data',
          key: storeKey,
        }
      )
    )
    window && window.URL.revokeObjectURL(image.preview)
  }

  onZoomChange = e => {
    this.setState({ zoom: parseFloat(e.target.value) })
  }

  onImageChange = ctx => {
    if (!this.state.image) return
    const { onImageChange } = this.props
    if (onImageChange) {
      if (this.state.isUploadDisabled) return onImageChange(ctx)
      onImageChange(
        ctx,
        this.state.image,
        this.avatarEditor.current.getCroppingRect()
      )
    }
  }

  setZoomInput = element => {
    this.zoomInput = element
  }

  changeZoom(direction) {
    const factor = 10 // Slider step is too low for button usage
    const step = parseFloat(this.zoomInput.getAttribute('step'))
    const zoom = this.state.zoom + step * factor * direction

    const min = parseFloat(this.zoomInput.getAttribute('min'))
    const max = parseFloat(this.zoomInput.getAttribute('max'))
    if (zoom >= min && zoom <= max) {
      this.setState({ zoom })
    }
  }

  increment = () => this.changeZoom(1)
  decrement = () => this.changeZoom(-1)

  render() {
    const {
      border,
      borderRadius,
      className,
      height,
      maxSize,
      width,
      onImageChange,
      hasExistingImage,
    } = this.props
    const {
      image,
      dragging,
      isUploadDisabled,
      readOnly,
      size,
      zoom,
    } = this.state

    return (
      <div className="field">
        <div className={classnames('upload-thumb', className)}>
          <Dropzone
            className={classnames('dropzone', {
              'has-image': Boolean(image),
              'no-drag': readOnly,
            })}
            onDragEnter={this.handleDragStart}
            onDragLeave={this.handleDragStop}
            onDrop={this.handleDrop}
            disableClick={Boolean(image || readOnly)}>
            {!image && (
              <div
                className={`drag-n-drop ${dragging ? 'dragged' : ''}`}
                style={{ borderRadius, width, height }}>
                Cliquez ou glissez-déposez pour charger une image
              </div>
            )}
            <AvatarEditor
              ref={this.avatarEditor}
              width={width}
              height={height}
              scale={zoom}
              border={border}
              borderRadius={borderRadius}
              color={[255, 255, 255, readOnly || !image ? 1 : 0.6]}
              image={image}
              onImageChange={this.onImageChange}
            />
            {!readOnly && image && (
              <div id="zoomControl">
                <button
                  onClick={this.decrement}
                  className="change-zoom decrement">
                  -
                </button>
                <input
                  ref={this.setZoomInput}
                  className="zoom level-left"
                  type="range"
                  min="0.1"
                  max="3"
                  step="0.01"
                  value={zoom}
                  onChange={this.onZoomChange}
                />
                <button
                  onClick={this.increment}
                  className="change-zoom increment">
                  +
                </button>
              </div>
            )}
          </Dropzone>
          <nav className="field content">
            {isUploadDisabled && (
              <p className="has-text-danger">
                {`Votre image trop volumineuse : ${size.toFixed(
                  2
                )} > ${maxSize}Mo`}
              </p>
            )}
            <div className="field is-grouped is-grouped-centered">
              <div className="control">
                {readOnly && (
                  <button
                    onClick={e => this.setState({ isEdited: true })}
                    className="button is-primary">
                    Modifier l'image
                  </button>
                )}
                {!onImageChange && // upload is managed by child component
                  !readOnly &&
                  image && (
                    <button
                      onClick={this.onUploadClick}
                      className="button is-primary"
                      disabled={isUploadDisabled}>
                      Enregistrer
                    </button>
                  )}
              </div>
              {!readOnly && image && !this.props.image && (
                <div className="control">
                  <button
                    onClick={e =>
                      this.setState({
                        image: null,
                        dragging: false,
                        isUploadDisabled: false,
                      })
                    }
                    className="button is-primary is-outlined">
                    Retirer l'image
                  </button>
                </div>
              )}
              {!readOnly && hasExistingImage && (
                <div className="control">
                  <button
                    onClick={e =>
                      this.setState({ isEdited: false, dragging: false })
                    }
                    className="button is-primary is-outlined">
                    Annuler la modification
                  </button>
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
  index: 0,
  maxSize: 10, // in MB
  width: 250,
}

export default connect()(UploadThumb)
