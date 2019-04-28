import classnames from 'classnames'
import L from 'leaflet'
import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import Autocomplete from 'react-autocomplete'
import { Map, Marker, TileLayer } from 'react-leaflet'

import getAddressSuggestions from './getAddressSuggestions'
import sanitizeCoordinates from './sanitizeCoordinates'
import { FRANCE_POSITION } from './positions'
import { ROOT_PATH } from 'utils/config'

const customIcon = new L.Icon({
  iconUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconRetinaUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconSize: [21, 30],
  iconAnchor: [10, 30],
  popupAnchor: null,
})

class Address extends Component {
  constructor(props) {
    super(props)
    this.state = {
      draggable: true,
      isLoading: false,
      marker: null,
      position: props.initialPosition,
      value: '',
      selectedAddress: null,
      suggestions: [],
    }
    this.refmarker = React.createRef()
    this.onDebouncedFetchSuggestions = debounce(
      this.fetchSuggestions,
      props.debounceTimeout
    )
  }

  static getDerivedStateFromProps = (newProps, currentState) => {
    const latitude = sanitizeCoordinates(newProps.latitude)
    const longitude = sanitizeCoordinates(newProps.longitude)

    const nextPosition = {
      latitude: latitude || newProps.defaultInitialPosition.latitude,
      longitude: longitude || newProps.defaultInitialPosition.longitude,
      zoom:
        latitude && longitude
          ? newProps.zoom
          : newProps.defaultInitialPosition.zoom,
    }

    return Object.assign(
      {},
      currentState,
      {
        position: nextPosition,
        value:
          newProps.value === '' ? '' : newProps.value || currentState.value,
      },
      latitude && longitude
        ? {
            suggestions: currentState.selectedAddress
              ? []
              : currentState.suggestions,
            marker: {
              latitude,
              longitude,
            },
          }
        : null
    )
  }

  toggleDraggable = () => {
    this.setState({ draggable: !this.state.draggable })
  }

  onMarkerDragend = () => {
    const { onMarkerDragend } = this.props
    const { lat, lng } = this.refmarker.current.leafletElement.getLatLng()
    this.setState({
      marker: {
        latitude: lat,
        longitude: lng,
      },
      suggestions: [],
    })
    onMarkerDragend({
      address: 'TBD',
      city: 'TBD',
      latitude: lat,
      longitude: lng,
      postalCode: 'TBD',
      selectedAddress: null,
    })
  }

  onTextChange = event => {
    const { onTextChange } = this.props
    const value = event.target.value
    this.setState({ value })

    const values = {
      address: value,
      city: null,
      latitude: null,
      longitude: null,
      postalCode: null,
      selectedAddress: null,
    }

    onTextChange(values)
    this.onDebouncedFetchSuggestions(value)
  }

  onSuggestionSelect = (value, item) => {
    const { onSuggestionSelect, zoom } = this.props
    if (item.placeholder) return
    this.setState({
      value,
      position: {
        latitude: item.latitude,
        longitude: item.longitude,
        zoom,
      },
      marker: {
        latitude: item.latitude,
        longitude: item.longitude,
      },
      selectedAddress: value,
    })
    onSuggestionSelect(item)
  }

  fetchSuggestions = value => {
    const { maxSuggestions, placeholder } = this.props
    this.setState({ isLoading: true })

    getAddressSuggestions(value, maxSuggestions).then(result => {
      if (result.error) {
        return
      }

      if (result.data.length === 0) {
        this.setState({
          isLoading: false,
        })
        return
      }

      const dataWithSelectedAddress = result.data.map(datum =>
        Object.assign({ selectedAddress: datum.address }, datum)
      )

      const defaultSuggestion = {
        label: placeholder,
        placeholder: true,
        id: 'placeholder',
      }

      const suggestions = dataWithSelectedAddress.concat(defaultSuggestion)

      this.setState({
        isLoading: false,
        selectedAddress: null,
        suggestions,
      })
    })
  }

  renderInput() {
    const { className, id, name, placeholder, readOnly, required } = this.props
    const { isLoading, suggestions, value } = this.state

    if (readOnly) {
      return (
        <input
          className={className}
          name={name}
          readOnly={readOnly}
          value={value}
        />
      )
    }

    return (
      <Fragment>
        <Autocomplete
          autocomplete="street-address"
          getItemValue={value => value.label}
          inputProps={{
            className: className || `input`,
            id,
            placeholder,
            readOnly,
            required,
          }}
          items={suggestions}
          name={name}
          onChange={this.onTextChange}
          onSelect={this.onSuggestionSelect}
          readOnly={readOnly}
          renderItem={({ id, label, placeholder }, highlighted) => (
            <div
              className={classnames({
                item: true,
                highlighted,
                placeholder,
              })}
              key={id}>
              {label}
            </div>
          )}
          renderMenu={children => (
            <div
              className={classnames('menu', { empty: children.length === 0 })}>
              {children}
            </div>
          )}
          value={this.props.value || value}
          wrapperProps={{ className: 'input-wrapper' }}
        />
        <button
          className={classnames('button is-loading', {
            'is-invisible': !isLoading,
          })}
        />
      </Fragment>
    )
  }

  render() {
    const { withMap } = this.props
    const { marker, position } = this.state

    if (!withMap) return this.renderInput()
    const { latitude, longitude, zoom } = position

    return (
      <div className="address">
        {this.renderInput()}
        <Map center={[latitude, longitude]} zoom={zoom} className="map">
          <TileLayer
            // url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          />
          {marker && (
            <Marker
              draggable
              onDragend={this.onMarkerDragend}
              position={[marker.latitude, marker.longitude]}
              icon={customIcon}
              ref={this.refmarker}
              alt={[marker.latitude, marker.longitude].join('-')}
            />
          )}
        </Map>
      </div>
    )
  }
}

Address.defaultProps = {
  debounceTimeout: 300,
  defaultInitialPosition: FRANCE_POSITION,
  latitude: null,
  longitude: null,
  maxSuggestions: 5,
  name: null,
  onMarkerDragend: () => {},
  onSuggestionSelect: () => {},
  onTextChange: () => {},
  placeholder: "Sélectionnez l'adresse lorsqu'elle est proposée.",
  withMap: false,
  zoom: 15,
}

Address.propTypes = {
  debounceTimeout: PropTypes.number,
  defaultInitialPosition: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
    zoom: PropTypes.number,
  }),
  latitude: PropTypes.number,
  longitude: PropTypes.number,
  maxSuggestions: PropTypes.number,
  name: PropTypes.string,
  onMarkerDragend: PropTypes.func,
  onSuggestionSelect: PropTypes.func,
  onTextChange: PropTypes.func,
  placeholder: PropTypes.string,
  withMap: PropTypes.bool,
  zoom: PropTypes.number,
}

export default Address
