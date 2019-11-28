import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import AvatarEditor from 'react-avatar-editor'

const IMAGE_MAX_SIZE = 10 // in MB

export const isImageTooLarge = sizeInMo => {
  return sizeInMo > IMAGE_MAX_SIZE
}

export const computeNewZoom = (current, min, max, step, factor, direction) => {
  const zoom = current + step * factor * direction

  if (zoom >= min && zoom <= max) {
    return zoom
  }

  return current
}

class UploadThumb extends PureComponent {
  constructor() {
    super()
    this.avatarEditor = React.createRef()
    this.handleSetZoomInput = React.createRef()
    this.state = {
      readOnly: false,
      image: null,
      isUploadDisabled: false,
      zoom: 1,
    }
  }

  static getDerivedStateFromProps(props, prevState) {
    const readOnly = props.hasExistingImage
    return {
      readOnly,
      image: props.image || prevState.image,
    }
  }

  handleOnZoomChange = event => {
    this.setState({ zoom: parseFloat(event.target.value) })
  }

  handleOnImageChange = ctx => {
    const { image, isUploadDisabled } = this.state
    if (!image) return
    const { onImageChange } = this.props
    const getCroppingRect = this.avatarEditor.current.getCroppingRect()
    if (isUploadDisabled) return onImageChange(ctx)

    onImageChange(ctx, image, getCroppingRect)
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

  handleIncrement = () => this.changeZoom(1)

  handleDecrement = () => this.changeZoom(-1)

  render() {
    const { border, borderRadius, className, height, maxSize, width } = this.props
    const { image, readOnly, zoom } = this.state
    let sizeInMo

    if (image) {
      sizeInMo = image.size / 1000000
    }

    const showAlert = isImageTooLarge(sizeInMo)

    return (
      <div className="field">
        <div className={classnames('upload-thumb', className)}>
          <div
            className={classnames('editor-zone', {
              'has-image': Boolean(image),
              'no-drag': readOnly,
            })}
          >
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
            {!readOnly && (
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
          </div>
          <nav className="field content">
            {showAlert && (
              <p className="has-text-danger">
                {`Votre image trop volumineuse, elle doit faire moins de ${maxSize} Mo.`}
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
