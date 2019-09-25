import React, { Fragment, PureComponent } from 'react'
import Thumb from '../../../layout/Thumb'
import { PROVIDER_ICONS } from '../../Venue/VenueProvidersManager/VenueProviderItem/utils/providerIcons'
import Icon from '../../../layout/Icon'
import ReactTooltip from 'react-tooltip'
import PropTypes from 'prop-types'

class TiteLiveInformation extends PureComponent {
  componentDidMount() {
    ReactTooltip.rebuild()
  }

  render() {
    const { offererId, thumbUrl, venueId } = this.props
    const providerIcon = PROVIDER_ICONS['TiteLiveStocks']

    const tooltipContent =
      '<div>' +
      '<p>Vous pouvez modifier vos choix de synchronisation sur' +
      " <a href='/structures/" +
      offererId +
      '/lieux/' +
      venueId +
      "'>la page du lieu</a>" +
      '  qui présente cette offre, dans la section "Importation d’offres".' +
      '</p>' +
      '</div>'

    return (
      <Fragment>
        <div className="titelive-information">
          <div className="titelive-thumb">
            <Thumb
              alt="offre"
              src={thumbUrl}
            />
          </div>
          <div className="titelive-details">
            <div className="titelive-header">
              <Icon svg={providerIcon} />
              <div className="titelive-title">
                {'Offre synchronisée avec Tite Live'}
                <span
                  className="button"
                  data-place="bottom"
                  data-tip={tooltipContent}
                  data-type="info"
                >
                  <Icon svg="picto-info" />
                </span>
              </div>
            </div>
            <div className="titelive-explanation">
              <p>
                {'Le visuel par défaut, les informations et le stock de cette offre sont synchronisés' +
                  ' avec les données Tite Live tous les soirs. De ce fait, seule sa description est modifiable,' +
                  ' pour vos besoins d’éditorialisation pour le pass Culture.'}
              </p>
            </div>
          </div>
        </div>
      </Fragment>
    )
  }
}

TiteLiveInformation.defaultProps = {
  thumbUrl: undefined,
}

TiteLiveInformation.propTypes = {
  offererId: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
  venueId: PropTypes.string.isRequired,
}

export default TiteLiveInformation
