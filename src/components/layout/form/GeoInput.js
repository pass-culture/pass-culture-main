import classnames from 'classnames'
import L from 'leaflet'
import debounce from 'lodash.debounce'
import { ROOT_PATH } from 'pass-culture-shared'
import React, { Component } from 'react'
import Autocomplete from 'react-autocomplete'
import { Map, Marker, TileLayer } from 'react-leaflet'

const customIcon = new L.Icon({
    iconUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
    iconRetinaUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
    iconSize: [21, 30],
    iconAnchor: [10, 30],
    popupAnchor: null,
});


class GeoInput extends Component {
  constructor(props) {
    super(props)
    this.state = {
      draggable: true,
      marker: null,
      position: props.initialPosition,
      value: '',
      suggestions: null,
    }
    this.refmarker = React.createRef()
    this.onDebouncedFetchSuggestions = debounce(
      this.fetchSuggestions,
      props.debounceTimeout
    )
  }

  static defaultProps = {
    debounceTimeout: 300,
    showMap: true,
    maxSuggestions: 5,
    placeholder: 'Sélectionnez l\'adresse lorsqu\'elle est proposée.',
    zoom: 15,
    defaultInitialPosition: { // Displays France
      latitude: 46.98025235521883,
      longitude: 1.9335937500000002,
      zoom: 5,
    }
  }

  static extraFormData = ['latitude', 'longitude']

  static getDerivedStateFromProps = (newProps, currentState) => {
    return Object.assign({}, currentState, {
      position: {
        latitude: newProps.latitude || newProps.defaultInitialPosition.latitude,
        longitude: newProps.longitude || newProps.defaultInitialPosition.longitude,
        zoom: newProps.latitude && newProps.longitude ? newProps.zoom : newProps.defaultInitialPosition.zoom
      }
    }, newProps.latitude && newProps.longitude ? {
      suggestions: [],
      marker: {
        latitude: newProps.latitude,
        longitude: newProps.longitude,
      }
    } : null)
  }

  toggleDraggable = () => {
    this.setState({ draggable: !this.state.draggable })
  }

  updatePosition = () => {
    const { lat, lng } = this.refmarker.current.leafletElement.getLatLng()
    this.setState({
      marker: {
        latitude: lat,
        longitude: lng
      },
    })
    this.props.onChange({
      latitude: lat,
      longitude: lng,
    })
  }

  onTextChange = (e) => {
    const value = e.target.value
    this.setState({
      value,
    })
    this.onDebouncedFetchSuggestions(value)
    this.props.onChange({[this.props.name]: value})
  }

  onSelect = (value, item) => {
    if (item.placeholder) return
    this.setState({
      value,
      position: {
        latitude: item.latitude,
        longitude: item.longitude,
        zoom: this.props.zoom,
      },
      marker: {
        latitude: item.latitude,
        longitude: item.longitude,
      }
    })

    this.props.onChange(item)
  }

  fetchSuggestions = value => {
    if (value.split(/\s/).filter(v => v).length < 2) // start querying if more than 1 word
      return this.setState({
        suggestions: null,
      })
    fetch(`https://api-adresse.data.gouv.fr/search/?limit=${this.props.maxSuggestions}&q=${value}`)
      .then(response => response.json())
      .then(data => {
        this.setState({
          suggestions: data.features.map(f => ({
            latitude: f.geometry.coordinates[1],
            longitude: f.geometry.coordinates[0],
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
      marker,
      position,
      suggestions,
      value,
    } = this.state

    const defaultSuggestion = {
      label: placeholder,
      placeholder: true,
      id: 'placeholder',
    }


    const input = <Autocomplete
      autocomplete='street-address'
      getItemValue={value => value.label}
      inputProps={{
        className: className || 'input',
        id,
        placeholder,
        readOnly,
        required,
      }}
      items={[].concat(suggestions || defaultSuggestion)}
      onChange={this.onTextChange}
      onSelect={this.onSelect}
      readOnly={readOnly}
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
      renderMenu={children => (
        <div className={classnames('menu', {empty: children.length === 0})}>
          {children}
        </div>
      )}
      value={this.props.value || value}
      wrapperProps={{ className: 'input-wrapper' }}
    />

    if (!this.props.withMap) return input
    const {
      latitude, longitude, zoom
    } = position

    return (
      <div className='form-geo'>
        {input}
        <Map
          center={[latitude, longitude]}
          zoom={zoom}
          className='map'
          >
          <TileLayer
            // url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          />
          {marker &&
            <Marker
              draggable
              onDragend={this.updatePosition}
              position={[marker.latitude, marker.longitude]}
              icon={customIcon}
              ref={this.refmarker}>
            </Marker>
          }
        </Map>
      </div>
    )
  }
}

export default GeoInput