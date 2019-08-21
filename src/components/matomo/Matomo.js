import PropTypes from 'prop-types'

const Matomo = ({ location, user }) => {
  const Matomo = window._paq || []

  let userId = 'Anonymous'
  if (user) {
    userId = user.id
  }

  Matomo.push(['setCustomUrl', location.pathname])
  Matomo.push(['setDocumentTitle', document.title])
  Matomo.push(['setUserId', userId])

  return null
}

Matomo.defaultProps = {
  user: {},
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
  user: PropTypes.shape(),
}

export default Matomo
