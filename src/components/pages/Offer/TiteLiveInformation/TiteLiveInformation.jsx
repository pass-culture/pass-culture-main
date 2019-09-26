import React, { Fragment, PureComponent } from 'react'
import Thumb from '../../../layout/Thumb'
import Icon from '../../../layout/Icon'
import ReactTooltip from 'react-tooltip'
import PropTypes from 'prop-types'
import { PROVIDER_ICONS } from '../../../utils/providers'

class TiteLiveInformation extends PureComponent {
  componentDidMount() {
    ReactTooltip.rebuild()
  }

  render() {
    const { offererId, productName, thumbUrl, venueId } = this.props
    const providerIcon = PROVIDER_ICONS['TiteLiveStocks']

    const thumbAltDescription = 'couverture du livre ' + productName
    const tooltip =
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
              alt={thumbAltDescription}
              src={thumbUrl}
            />
          </div>
          <div className="titelive-details">
            <div className="titelive-header">
              <Icon svg={providerIcon} />
              <div className="titelive-title">
                <h1>
                  {'Offre synchronisée avec Tite Live'}
                </h1>
                <span
                  className="button"
                  data-place="bottom"
                  data-tip={tooltip}
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
  thumbUrl: null,
}

TiteLiveInformation.propTypes = {
  offererId: PropTypes.string.isRequired,
  productName: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
  venueId: PropTypes.string.isRequired,
}

export default TiteLiveInformation
