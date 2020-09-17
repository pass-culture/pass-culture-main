import classnames from 'classnames'
import L from 'leaflet'
import debounce from 'lodash.debounce'
import { BasicInput } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import Autocomplete from 'react-autocomplete'
import { Map, Marker, TileLayer } from 'react-leaflet'

import { ROOT_PATH } from '../../utils/config'
import sanitizeCoordinates from '../pages/Venue/fields/LocationFields/utils/sanitizeCoordinates'

const customIcon = new L.Icon({
  iconUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconRetinaUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconSize: [21, 30],
  iconAnchor: [10, 30],
  popupAnchor: null,
})

class GeoInput extends Component {
  constructor(props) {
    super(props)
    this.state = {
      draggable: true,
      isLoading: false,
      marker: null,
      position: props.initialPosition,
      value: '',
      suggestions: [],
    }
    this.refmarker = React.createRef()
    this.onDebouncedFetchSuggestions = debounce(this.fetchSuggestions, props.debounceTimeout)
  }

  static getDerivedStateFromProps = (newProps, currentState) => {
    const latitude = sanitizeCoordinates(newProps.latitude)
    const longitude = sanitizeCoordinates(newProps.longitude)

    return Object.assign(
      {},
      currentState,
      {
        position: {
          latitude: latitude || newProps.defaultInitialPosition.latitude,
          longitude: longitude || newProps.defaultInitialPosition.longitude,
          zoom: latitude && longitude ? newProps.zoom : newProps.defaultInitialPosition.zoom,
        },
      },
      latitude && longitude
        ? {
            suggestions: [],
            marker: {
              latitude: latitude,
              longitude: longitude,
            },
          }
        : null
    )
  }

  toggleDraggable = () => {
    const { draggable } = this.state

    this.setState({ draggable: !draggable })
  }

  handleUpdatePosition = () => {
    const { onMergeForm } = this.props
    const { lat, lng } = this.refmarker.current.leafletElement.getLatLng()
    this.setState({
      marker: {
        latitude: lat,
        longitude: lng,
      },
    })
    onMergeForm({
      latitude: lat,
      longitude: lng,
    })
  }

  handleOnTextChange = event => {
    const { name, onMergeForm } = this.props
    const value = event.target.value
    this.setState({ value })
    this.onDebouncedFetchSuggestions(value)
    onMergeForm(
      {
        address: null,
        city: null,
        geo: null,
        latitude: null,
        longitude: null,
        [name]: value,
        postalCode: null,
      },
      { event }
    )
  }

  handleOnSelect = (value, item) => {
    const { onMergeForm, zoom } = this.props
    if (item.placeholder) return
    this.setState({
      value,
      position: {
        latitude: item.latitude,
        longitude: item.longitude,
        zoom: zoom,
      },
      marker: {
        latitude: item.latitude,
        longitude: item.longitude,
      },
    })
    onMergeForm(item)
  }

  fetchSuggestions = value => {
    const { maxSuggestions, placeholder } = this.props
    const wordsCount = value.split(/\s/).filter(v => v).length
    if (wordsCount < 2)
      return this.setState({
        suggestions: [],
      })

    this.setState({ isLoading: true })

    fetch(`https://api-adresse.data.gouv.fr/search/?limit=${maxSuggestions}&q=${value}`)
      .then(response => response.json())
      .then(data => {
        const defaultSuggestion = {
          label: placeholder,
          placeholder: true,
          id: 'placeholder',
        }

        const fetchedSuggestions = data.features.map(f => ({
          address: f.properties.name,
          city: f.properties.city,
          geo: f.geometry.coordinates,
          id: f.properties.id,
          latitude: f.geometry.coordinates[1],
          longitude: f.geometry.coordinates[0],
          label: f.properties.label,
          postalCode: f.properties.postcode,
        }))

        const suggestions = fetchedSuggestions.concat(defaultSuggestion)

        this.setState({
          isLoading: false,
          suggestions,
        })
      })
  }

  getItemValue = value => value.label

  renderAutocomplete = ({ id, label, placeholder }, highlighted) => (
    <div
      className={classnames({
        item: true,
        highlighted,
        placeholder,
      })}
      key={id}
    >
      {label}
    </div>
  )

  renderAutocompleteMenu = children => (
    <div className={classnames('menu', { empty: children.length === 0 })}>
      {children}
    </div>
  )

  render() {
    const { className, id, placeholder, readOnly, required, size, value:propsValue, withMap } = this.props

    const { isLoading, marker, position, suggestions, value:stateValue } = this.state

    const $input = readOnly ? (
      <BasicInput {...this.props} />
    ) : (
      <Fragment>
        <Autocomplete
          autocomplete="street-address"
          getItemValue={this.getItemValue}
          inputProps={{
            className: className || `input is-${size}`,
            id,
            placeholder,
            readOnly,
            required,
          }}
          items={suggestions}
          onChange={this.handleOnTextChange}
          onSelect={this.handleOnSelect}
          readOnly={readOnly}
          renderItem={this.renderAutocomplete}
          renderMenu={this.renderAutocompleteMenu}
          value={propsValue || stateValue}
          wrapperProps={{ className: 'input-wrapper' }}
        />
        <button
          className={classnames('button is-loading', {
            'is-invisible': !isLoading,
          })}
          type="button"
        />
      </Fragment>
    )

    if (!withMap) return $input
    const { latitude, longitude, zoom } = position

    return (
      <div className="geo-input">
        {$input}
        <Map
          center={[latitude, longitude]}
          className="map"
          zoom={zoom}
        >
          <TileLayer
            // url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          />
          {marker && (
            <Marker
              alt={[marker.latitude, marker.longitude].join('-')}
              draggable
              icon={customIcon}
              onDragend={this.handleUpdatePosition}
              position={[marker.latitude, marker.longitude]}
              ref={this.refmarker}
            />
          )}
        </Map>
      </div>
    )
  }
}

GeoInput.defaultProps = {
  debounceTimeout: 300,
  defaultInitialPosition: {
    latitude: 46.98025235521883,
    longitude: 1.9335937500000002,
    zoom: 5,
  },
  maxSuggestions: 5,
  placeholder: 'Sélectionnez l’adresse lorsqu’elle est proposée.',
  withMap: false,
  zoom: 15,
}

GeoInput.propTypes = {
  className: PropTypes.string.isRequired,
  debounceTimeout: PropTypes.number,
  defaultInitialPosition: PropTypes.shape(),
  id: PropTypes.string.isRequired,
  initialPosition: PropTypes.string.isRequired,
  maxSuggestions: PropTypes.number,
  name: PropTypes.string.isRequired,
  onMergeForm: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.string.isRequired,
  required: PropTypes.string.isRequired,
  size: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  withMap: PropTypes.bool,
  zoom: PropTypes.number,
}

export default GeoInput
