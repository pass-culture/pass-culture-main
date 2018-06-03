import React, { Component } from 'react'
import AvatarEditor from 'react-avatar-editor'
import Dropzone from 'react-dropzone'

import Icon from './Icon'

class FormThumb extends Component {

  constructor() {
    super()
    this.state = {
      image: null,
      zoom: 1,
    }
  }

  handleDrop = dropped => {
    this.setState({ image: dropped[0] })
  }

  render () {
    const {
      image,
      zoom
    } = this.state

    return (
      <Dropzone
        className={`input form-thumb ${image && 'has-image'}`}
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
            <p className="drag-n-drop">
              Cliquez ou glissez-déposez pour charger une image
            </p>
          )
        }
        <AvatarEditor
          width={250}
          height={250}
          scale={zoom}
          border={50}
          borderRadius={250}
          color={[255, 255, 255, image ? 0.6 : 1]}
          image={image}
        />
        {
          image && (
            <input
              className="zoom"
              type="range"
              min="1"
              max="2"
              step="0.01"
              value={zoom}
              onChange={e => this.setState({zoom: parseFloat(e.target.value)})}
            />
          )
        }
      </Dropzone>
    )
  }
}

export default FormThumb
