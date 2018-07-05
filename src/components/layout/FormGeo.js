import React, { Component } from 'react'
import { Map, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet';
import Autocomplete from 'react-autocomplete'

import Icon from './Icon'
import FormInput from './FormInput'
import { ROOT_PATH } from '../../utils/config'

const customIcon = new L.Icon({
    iconUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
    iconRetinaUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
    iconSize: [21, 30],
    iconAnchor: [10, 30],
    iconAnchor: null,
    popupAnchor: null,
    // shadowUrl: null,
    // shadowSize: null,
    // shadowAnchor: null,
});


class FormGeo extends Component {
  constructor() {
    super()
    this.state = {
      draggable: true,
      marker: {
        lat: 43.60346942785451,
        lng: 1.4562785625457764,
      },
      value: '',
    }
    this.refmarker = React.createRef()
  }

  static defaultProps = {
    showMap: true,
    initialPosition: {
      lat: 46.98025235521883,
      lng: 1.9335937500000002,
      zoom: 5,
    }
  }

  toggleDraggable = () => {
    this.setState({ draggable: !this.state.draggable })
  }

  updatePosition = () => {

    const { lat, lng } = this.refmarker.current.leafletElement.getLatLng()
    this.setState({
      marker: { lat, lng },
    })
  }

  onChange = (e) => {
    this.setState({
      value: e.target.value
    })
  }

  onSelect = (value) => {
    this.setState({
      value
    })
  }

  render() {
    const {
      className,
      id,
      readOnly,
      required,
      placeholder,
    } = this.props

    const {
      value
    } = this.state


    const input = <Autocomplete

        className={className || 'input'}
        id={id}
        onChange={this.onChange}
        placeholder={placeholder}
        readOnly={readOnly}
        required={required}
        type='text'
        value={value}
        getItemValue={value => value}
        renderMenu={children => (
          <div className="menu">
            {children}
          </div>
        )}
        renderItem={(item, isHighlighted) => (
          <div
            className={`item ${isHighlighted ? 'item-highlighted' : ''}`}
            key={item}
          >{item}</div>
        )}
        items={['hey', 'you', 'how', 'are', 'you?']}
        onSelect={this.onSelect}
      />

    if (!this.props.showMap) return input
    const markerPosition = [this.state.marker.lat, this.state.marker.lng]
    const {
      lat, lng, zoom
    } = this.props.initialPosition

    return (
      <div className='form-geo'>
        {input}
        <Map
          center={[lat, lng]}
          zoom={zoom}
          className='input-map'
          >
          <TileLayer
            // url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          />
          <Marker
            draggable={this.state.draggable}
            onDragend={this.updatePosition}
            position={markerPosition}
            icon={customIcon}
            ref={this.refmarker}>
            <Popup minWidth={90}>
              <span onClick={this.toggleDraggable}>
                {this.state.draggable ? 'DRAG MARKER' : 'MARKER FIXED'}
              </span>
            </Popup>
          </Marker>
        </Map>
      </div>
    )
  }
}

export default FormGeo
