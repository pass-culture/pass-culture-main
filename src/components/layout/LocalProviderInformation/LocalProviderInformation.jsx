import React, { PureComponent } from 'react'
import Thumb from '../Thumb'
import Icon from '../Icon'
import ReactTooltip from 'react-tooltip'
import PropTypes from 'prop-types'

class LocalProviderInformation extends PureComponent {
  componentDidMount() {
    ReactTooltip.rebuild()
  }

  render() {
    const { offerName, offererId, providerInfo, thumbUrl, venueId } = this.props

    const thumbAltDescription = 'couverture du livre ' + offerName
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
      <div className="provider-information">
        <div className="provider-thumb">
          <Thumb
            alt={thumbAltDescription}
            src={thumbUrl}
          />
        </div>
        <div className="provider-details">
          <div className="provider-header">
            <Icon
              height="64px"
              svg={providerInfo.icon}
              width="64px"
            />
            <div className="provider-title">
              <h3>
                {`Offre synchronisée avec ${providerInfo.name}`}
              </h3>
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
          <div className="provider-explanation">
            <p>
              {'Le visuel par défaut, les informations et le stock de cette offre sont synchronisés' +
              ` avec les données ${providerInfo.name} tous les soirs.`}
            </p>
          </div>
        </div>
      </div>
    )
  }
}

LocalProviderInformation.defaultProps = {
  thumbUrl: null,
}

LocalProviderInformation.propTypes = {
  offerName: PropTypes.string.isRequired,
  offererId: PropTypes.string.isRequired,
  providerInfo: PropTypes.shape().isRequired,
  thumbUrl: PropTypes.string,
  venueId: PropTypes.string.isRequired,
}

export default LocalProviderInformation
