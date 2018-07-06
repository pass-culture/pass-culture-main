import React, { Component } from 'react'
import { Map, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import Autocomplete from 'react-autocomplete'
import classnames from 'classnames'
import debounce from 'lodash.debounce'

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
  constructor(props) {
    super(props)
    this.state = {
      draggable: true,
      marker: {
        lat: 43.60346942785451,
        lng: 1.4562785625457764,
      },
      value: '',
      suggestions: [{
        label: 'Sélectionnez l\'adresse lorsqu\'elle est proposée.',
        placeholder: true,
        id: 'placeholder',
      }]
    }
    this.refmarker = React.createRef()
    this.onDebouncedFetchSuggestions = debounce(
      this.fetchSuggestions,
      props.debounceTimeout
    )
  }

  static defaultProps = {
    debounceTimeout: 500,
    showMap: true,
    maxSuggestions: 5,
    initialPosition: { // Displays France
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
    const value = e.target.value
    this.setState({
      value,
    })
    this.onDebouncedFetchSuggestions(value)
  }

  onSelect = (value) => {
    this.setState({
      value
    })
  }

  fetchSuggestions = value => {
    fetch(`https://api-adresse.data.gouv.fr/search/?limit=${this.props.maxSuggestions}&q=${value}`)
      .then(response => response.json())
      .then(data => {
        console.log(data)
        this.setState({
          suggestions: data.features.map(f => ({
            lat: f.geometry.coordinates[0],
            lng: f.geometry.coordinates[1],
            label: f.properties.label,
            address: f.properties.name,
            postalCode: f.properties.postcode,
            city: f.properties.city,
            id: f.properties.id,
          }))
        })
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
      suggestions,
      value,
    } = this.state


    const input = <Autocomplete
      inputProps={{
        className: className || 'input is-expanded',
        id: id,
        placeholder: placeholder,
        readOnly: readOnly,
        required: required,
      }}
      wrapperProps={{
        className: 'input-wrapper'
      }}
      onChange={this.onChange}
      value={value}
      getItemValue={value => value.label}
      renderMenu={children => (
        <div className="menu">
          {children}
        </div>
      )}
      renderItem={({id, label, placeholder}, highlighted) => (
        <div
          className={classnames({
            item: true,
            highlighted,
            placeholder,
          })}
          key={id}
        >{label}</div>
      )}
      items={suggestions}
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
          className='map'
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
          </Marker>
        </Map>
      </div>
    )
  }
}

export default FormGeo
