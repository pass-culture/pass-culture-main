import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'

const IMAGE_MAX_SIZE = 10 // in MB

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
    this.handleSetZoomInput = React.createRef()
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

  handleOnZoomChange = event => {
    this.setState({ zoom: parseFloat(event.target.value) })
  }

  handleOnImageChange = ctx => {
    console.log('CTX', ctx)
    const { image, isUploadDisabled } = this.state
    if (!image) return
    const { onImageChange } = this.props
    if (onImageChange) {
      if (isUploadDisabled) return onImageChange(ctx)

      onImageChange(ctx, image, this.avatarEditor.current.getCroppingRect())
    }
  }

  changeZoom(direction) {
    const { zoom } = this.state

    const factor = 10 // Slider step is too low for button usage
    const step = parseFloat(this.handleSetZoomInput.current.getAttribute('step'))
    const min = parseFloat(this.handleSetZoomInput.current.getAttribute('min'))
    const max = parseFloat(this.handleSetZoomInput.current.getAttribute('max'))

    const newZoom = computeNewZoom(zoom, min, max, step, factor, direction)

    this.setState({ zoom: newZoom })
  }

  handleOnChangeImageClick = () => this.setState({ isEdited: true })

  handleIncrement = () => this.changeZoom(1)

  handleDecrement = () => this.changeZoom(-1)

  render() {
    const { border, borderRadius, className, height, maxSize, width } = this.props
    const { dragging, image, isUploadDisabled, readOnly, size, zoom } = this.state
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
            {image && (
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
  height: 250,
  maxSize: IMAGE_MAX_SIZE,
  width: 250,
}

UploadThumb.propTypes = {
  border: PropTypes.number,
  borderRadius: PropTypes.number,
  className: PropTypes.string,
  hasExistingImage: PropTypes.bool.isRequired,
  height: PropTypes.number,
  image: PropTypes.oneOfType([PropTypes.string, PropTypes.shape()]).isRequired,
  maxSize: PropTypes.number,
  onImageChange: PropTypes.func.isRequired,
  width: PropTypes.number,
}

export default UploadThumb
