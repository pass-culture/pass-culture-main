import PropTypes from 'prop-types'

export const SearchHit = {
  offer: PropTypes.shape({
    dates: PropTypes.arrayOf(PropTypes.number),
    isDigital: PropTypes.bool,
    isDuo: PropTypes.bool,
    isEvent: PropTypes.bool,
    label: PropTypes.string,
    name: PropTypes.string,
    prices: PropTypes.arrayOf(PropTypes.number),
    thumbUrl: PropTypes.string,
  }),
  _geoloc: PropTypes.shape({
    lat: PropTypes.number,
    lng: PropTypes.number,
  }),
  venue: PropTypes.shape({
    departmentCode: PropTypes.string,
    name: PropTypes.string,
    publicName: PropTypes.string,
  }),
  objectID: PropTypes.string.isRequired,
}
