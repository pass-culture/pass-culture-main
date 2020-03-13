import { selectUserGeolocation } from '../../../../selectors/geolocationSelectors'
import { isGeolocationEnabled, isUserAllowedToSelectCriterion } from '../../../../utils/geolocation'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { Filters } from './Filters'

export const mapStateToProps = (state, ownProps) => {
  const geolocation = selectUserGeolocation(state)
  const redirectToSearchFiltersPage = () => {
    const { history } = ownProps
    const { location: { search = '' } } = history
    history.push(`/recherche-offres/resultats/filtres${search}`)
  }

  return {
    geolocation,
    isGeolocationEnabled: isGeolocationEnabled(geolocation),
    isUserAllowedToSelectCriterion,
    redirectToSearchFiltersPage,
  }
}

export default compose(
  connect(mapStateToProps)
)(Filters)
