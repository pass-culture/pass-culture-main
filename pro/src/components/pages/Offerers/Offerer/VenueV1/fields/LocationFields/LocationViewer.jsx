/* eslint no-undef: 0 */
import classnames from 'classnames'
import { Icon as LeafletIcon } from 'leaflet'
import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import Autocomplete from 'react-autocomplete'
import { MapContainer, Marker, TileLayer, useMap } from 'react-leaflet'

import { ROOT_PATH } from 'utils/config'

import getSuggestionsFromAddressAndMaxSuggestions from './selectors/getSuggestionsFromAddressAndMaxSuggestions'
import getSuggestionsFromLatitudeAndLongitude from './selectors/getSuggestionsFromLatitudeAndLongitude'
import { FRANCE_POSITION } from './utils/positions'
import sanitizeCoordinates from './utils/sanitizeCoordinates'

const markerIcon = new LeafletIcon({
  iconUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconRetinaUrl: `${ROOT_PATH}/icons/ico-geoloc-solid2.svg`,
  iconSize: [21, 30],
  iconAnchor: [10, 30],
  popupAnchor: null,
})

const ChangeView = ({ center, zoom }) => {
  const map = useMap()
  map.setView(center, zoom)
  return null
}

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class LocationViewer extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      inputValue: '',
      isLoading: false,
      marker: null,
      position: props.initialPosition,
      suggestions: [],
    }
    this.refmarker = React.createRef()
    this.onDebouncedFetchSuggestions = debounce(
      this.fetchSuggestions,
      props.debounceTimeout
    )
  }

  static getDerivedStateFromProps(newProps, state) {
    const latitude = sanitizeCoordinates(newProps.latitude)
    const longitude = sanitizeCoordinates(newProps.longitude)

    const hasCoordinates = latitude && longitude

    const nextPosition = {
      latitude: latitude || newProps.defaultInitialPosition.latitude,
      longitude: longitude || newProps.defaultInitialPosition.longitude,
      zoom: hasCoordinates
        ? newProps.zoom
        : newProps.defaultInitialPosition.zoom,
    }
    const isInputValueEmpty = newProps.value === ''
    const nextInputValue = isInputValueEmpty
      ? ''
      : newProps.value || state.inputValue
    const nextStateWithPositionAndInputValue = {
      inputValue: nextInputValue,
      position: nextPosition,
    }

    const nextStateWithSuggestionsAndMarker = hasCoordinates
      ? {
          suggestions: state.hasSelectedSuggestion ? [] : state.suggestions,
          marker: {
            latitude,
            longitude,
          },
        }
      : null

    return Object.assign(
      {},
      state,
      nextStateWithPositionAndInputValue,
      nextStateWithSuggestionsAndMarker
    )
  }

  handleOnMarkerDragend = () => {
    const { readOnly, onMarkerDragend } = this.props
    if (readOnly) {
      return
    }
    const { lat: latitude, lng: longitude } =
      this.refmarker.current.leafletElement.getLatLng()

    this.setState({
      marker: {
        latitude,
        longitude,
      },
      suggestions: [],
    })

    getSuggestionsFromLatitudeAndLongitude(latitude, longitude).then(result => {
      this.setState({
        isLoading: false,
      })

      if (result.error) {
        return
      }

      const hasOnlyOneSuggestion = result.data && result.data.length === 1
      if (hasOnlyOneSuggestion) {
        const suggestion = result.data[0]
        const { address, city, postalCode } = suggestion

        const location = {
          address,
          city,
          latitude,
          longitude,
          postalCode,
        }

        onMarkerDragend(location)
        return
      }

      const location = {
        address: null,
        city: null,
        latitude,
        longitude,
        postalCode: null,
      }

      onMarkerDragend(location)
    })
  }

  handleOnTextChange = event => {
    const { onTextChange: onTextChangeFromProps } = this.props
    const address = event.target.value
    this.setState({
      inputValue: address,
    })

    const location = {
      address,
      city: null,
      latitude: null,
      longitude: null,
      postalCode: null,
    }

    onTextChangeFromProps(location)
    this.onDebouncedFetchSuggestions(address)
  }

  handleOnSuggestionSelect = (address, location) => {
    const { onSuggestionSelect: onSuggestionSelectFromProps, zoom } = this.props
    const { latitude, longitude, placeholder } = location
    if (placeholder) return
    this.setState({
      inputValue: address,
      position: {
        latitude,
        longitude,
        zoom,
      },
      marker: {
        latitude,
        longitude,
      },
    })
    onSuggestionSelectFromProps(location)
  }

  fetchSuggestions = address => {
    const { maxSuggestions, placeholder } = this.props
    this.setState({ isLoading: true })

    // NOTE: CANNOT EXPRESS THIS WITH AWAIT ASYNC
    // BECAUSE this.props cannot be found in that case...
    // weird
    getSuggestionsFromAddressAndMaxSuggestions(address, maxSuggestions).then(
      result => {
        if (result.error) {
          return
        }

        const hasNoData = result.data.length === 0
        if (hasNoData) {
          this.setState({
            isLoading: false,
          })
          return
        }

        const defaultSuggestion = {
          label: placeholder,
          placeholder: true,
          id: 'placeholder',
        }

        const suggestions = result.data.concat(defaultSuggestion)
        this.setState({
          isLoading: false,
          suggestions,
        })
      }
    )
  }

  renderSuggestionsMenu = suggestionElements => {
    const empty = suggestionElements.length === 0
    return (
      <div className={classnames('menu', { empty })}>{suggestionElements}</div>
    )
  }

  renderSuggestion = ({ id, label, placeholder }, highlighted) => (
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

  onHandleGetItemValue = value => value.label

  renderInput() {
    const { className, id, name, placeholder, readOnly, required, value } =
      this.props
    const { inputValue, isLoading, suggestions } = this.state

    if (readOnly) {
      return (
        <input
          className={className}
          name={name}
          readOnly={readOnly}
          value={inputValue}
        />
      )
    }

    return (
      <Fragment>
        <Autocomplete
          autocomplete="street-address"
          getItemValue={this.onHandleGetItemValue}
          inputProps={{
            className: className || `input`,
            id,
            name,
            placeholder,
            readOnly,
            required,
          }}
          items={suggestions}
          onChange={this.handleOnTextChange}
          onSelect={this.handleOnSuggestionSelect}
          readOnly={readOnly}
          renderItem={this.renderSuggestion}
          renderMenu={this.renderSuggestionsMenu}
          value={value || inputValue}
          wrapperProps={{ className: 'input-wrapper' }}
        />
        {isLoading && <button className="button is-loading" type="button" />}
      </Fragment>
    )
  }

  render() {
    const { readOnly, withMap } = this.props
    const { marker, position } = this.state

    if (!withMap) return this.renderInput()
    const { latitude, longitude, zoom } = position
    return (
      <div className="location-viewer">
        {this.renderInput()}
        <MapContainer
          center={[latitude, longitude]}
          className="map"
          scrollWheelZoom={false}
          zoom={zoom}
        >
          <ChangeView center={[latitude, longitude]} zoom={zoom} />
          <TileLayer url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png" />
          {marker && (
            <Marker
              alt={[marker.latitude, marker.longitude].join('-')}
              draggable={!readOnly}
              icon={markerIcon}
              onDragend={this.handleOnMarkerDragend}
              position={[marker.latitude, marker.longitude]}
              ref={this.refmarker}
            />
          )}
        </MapContainer>
      </div>
    )
  }
}

LocationViewer.defaultProps = {
  debounceTimeout: 300,
  defaultInitialPosition: FRANCE_POSITION,
  maxSuggestions: 5,
  name: null,
  onMarkerDragend: () => {},
  onSuggestionSelect: () => {},
  onTextChange: () => {},
  placeholder: 'Sélectionnez l’adresse lorsqu’elle est proposée.',
  readOnly: true,
  withMap: false,
  zoom: 15,
}

LocationViewer.propTypes = {
  debounceTimeout: PropTypes.number,
  defaultInitialPosition: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
    zoom: PropTypes.number,
  }),
  maxSuggestions: PropTypes.number,
  name: PropTypes.string,
  onMarkerDragend: PropTypes.func,
  onSuggestionSelect: PropTypes.func,
  onTextChange: PropTypes.func,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  withMap: PropTypes.bool,
  zoom: PropTypes.number,
}

export default LocationViewer
