import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'
import { requestData } from 'redux-saga-data'

export function computeNewZoom(current, min, max, step, factor, direction) {
  const zoom = current + step * factor * direction

  if (zoom >= min && zoom <= max) {
    return zoom
  }

  return current
}

class UploadThumb extends Component {
  constructor() {
    super()
    this.avatarEditor = React.createRef()
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
    const readOnly = props.hasExistingImage && !prevState.isEdited
    return {
      readOnly,
      isDragging: prevState.isDragging,
      image: props.image || prevState.image,
    }
  }

  handleDragStart = () => {
    this.setState({
      dragging: true,
    })
  }

  handleDragStop = () => {
    this.setState({
      dragging: false,
    })
  }

  handleDrop = dropped => {
    const { maxSize } = this.props
    const image = dropped[0]
    // convert into MB
    const size = image.size / 1048576
    this.setState({
      isDragging: false,
      isUploadDisabled: size > maxSize,
      image,
      size,
    })
  }

  //  Utilisé ? Bouton Enregistrez invisible
  handleOnUploadClick = e => () => {
    const { collectionName, dispatch, entityId, index, storeKey } = this.props
    const { image, isUploadDisabled } = this.state
    this.setState({
      isEdited: false,
    })

    if (typeof image === 'string') return

    if (isUploadDisabled) return

    e.preventDefault()
    const formData = new FormData()
    formData.append('file', image)
    dispatch(
      requestData({
        apiPath: `/storage/thumb/${collectionName}/${entityId}/${index}`,
        body: formData,
        encode: 'multipart/form-data',
        method: 'POST',
        stateKey: storeKey,
      })
    )
    window && window.URL.revokeObjectURL(image.preview)
  }

  handleOnZoomChange = event => {
    this.setState({ zoom: parseFloat(event.target.value) })
  }

  handleOnImageChange = ctx => {
    const { image, isUploadDisabled } = this.state
    if (!image) return
    const { onImageChange } = this.props
    if (onImageChange) {
      if (isUploadDisabled) return onImageChange(ctx)

      onImageChange(ctx, image, this.avatarEditor.current.getCroppingRect())
    }
  }

  handleSetZoomInput = element => {
    this.zoomInput = element
  }

  // utilisé ???
  handleOnCancelModificationClick = () => this.setState({ isEdited: false, dragging: false })

  changeZoom(direction) {
    const { zoom } = this.state
    const factor = 10 // Slider step is too low for button usage
    const step = parseFloat(this.zoomInput.getAttribute('step'))
    const min = parseFloat(this.zoomInput.getAttribute('min'))
    const max = parseFloat(this.zoomInput.getAttribute('max'))

    const newZoom = computeNewZoom(zoom, min, max, step, factor, direction)

    this.setState({ zoom: newZoom })
  }

  handleOnChangeImageClick = () => this.setState({ isEdited: true })

  handleIncrement = () => this.changeZoom(1)

  handleDecrement = () => this.changeZoom(-1)

  handleOnRemoveImageClick = () =>
    this.setState({
      image: null,
      dragging: false,
      isUploadDisabled: false,
    })

  render() {
    const {
      border,
      borderRadius,
      className,
      height,
      image,
      maxSize,
      width,
      onImageChange,
      hasExistingImage,
    } = this.props
    const { dragging, isUploadDisabled, readOnly, size, zoom } = this.state

    return (
      <div className="field">
        <div className={classnames('upload-thumb', className)}>
          <Dropzone
            className={classnames('dropzone', {
              'has-image': Boolean(image),
              'no-drag': readOnly,
            })}
            disableClick={Boolean(image || readOnly)}
            onDragEnter={this.handleDragStart}
            onDragLeave={this.handleDragStop}
            onDrop={this.handleDrop}
          >
            {!image && (
              <div
                className={`drag-n-drop ${dragging ? 'dragged' : ''}`}
                style={{ borderRadius, width, height }}
              >
                {'Cliquez ou glissez-déposez pour charger une image'}
              </div>
            )}
            <AvatarEditor
              border={border}
              borderRadius={borderRadius}
              className="avatar editor"
              color={[255, 255, 255, readOnly || !image ? 1 : 0.6]}
              height={height}
              image={image}
              onImageChange={this.handleOnImageChange}
              ref={this.avatarEditor}
              scale={zoom}
              width={width}
            />
            <div className="barbapapa" />
            {!readOnly && image && (
              <div id="zoomControl">
                <button
                  className="change-zoom decrement"
                  onClick={this.handleDecrement}
                  type="button"
                >
                  <span>
                    {'-'}
                  </span>
                </button>

                <input
                  className="zoom level-left"
                  max="4"
                  min="1"
                  name="zoomLeft"
                  onChange={this.handleOnZoomChange}
                  ref={this.handleSetZoomInput}
                  step="0.01"
                  type="range"
                  value={zoom}
                />
                <button
                  className="change-zoom increment"
                  onClick={this.handleIncrement}
                  type="button"
                >
                  <span>
                    {'+'}
                  </span>
                </button>
              </div>
            )}
          </Dropzone>
          <nav className="field content">
            {isUploadDisabled && (
              <p className="has-text-danger">
                {`Votre image trop volumineuse : ${size.toFixed(2)} > ${maxSize}Mo`}
              </p>
            )}
            <div className="field is-grouped is-grouped-centered">
              <div className="control">
                {readOnly && (
                  <button
                    className="button is-primary"
                    onClick={this.handleOnChangeImageClick}
                    type="button"
                  >
                    {"Modifier l'image"}
                  </button>
                )}
                {!onImageChange && // upload is managed by child component
                  !readOnly &&
                  image && (
                    <button
                      className="button is-primary is-blabla"
                      disabled={isUploadDisabled}
                      onClick={this.handleOnUploadClick}
                      type="button"
                    >
                      {'Enregistrer'}
                    </button>
                  )}
              </div>
              {!readOnly && image && (
                <div className="control">
                  <button
                    className="button is-primary is-outlined"
                    onClick={this.handleOnRemoveImageClick}
                    type="button"
                  >
                    {"Retirer l'image"}
                  </button>
                </div>
              )}
              {!readOnly && hasExistingImage && (
                <div className="control">
                  <button
                    className="button is-primary is-outlined"
                    onClick={this.handleOnCancelModificationClick}
                    type="button"
                  >
                    {'Annuler la modification'}
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
  className: null,
  entityId: null,
  height: 250,
  index: 0,
  maxSize: 10, // in MB
  width: 250,
}

UploadThumb.propTypes = {
  border: PropTypes.number,
  borderRadius: PropTypes.number,
  className: PropTypes.string,
  collectionName: PropTypes.string.isRequired,
  dispatch: PropTypes.func.isRequired,
  entityId: PropTypes.string,
  hasExistingImage: PropTypes.bool.isRequired,
  height: PropTypes.number,
  image: PropTypes.oneOfType([PropTypes.string, PropTypes.shape()]).isRequired,
  index: PropTypes.number,
  maxSize: PropTypes.number,
  onImageChange: PropTypes.func.isRequired,
  storeKey: PropTypes.string.isRequired,
  width: PropTypes.number,
}

export default UploadThumb
