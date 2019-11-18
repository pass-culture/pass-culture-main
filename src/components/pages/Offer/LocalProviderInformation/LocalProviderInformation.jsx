import React, { Fragment, PureComponent } from 'react'
import Thumb from '../../../layout/Thumb'
import Icon from '../../../layout/Icon'
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
      <Fragment>
        <div className="provider-information">
          <div className="provider-thumb">
            <Thumb
              alt={thumbAltDescription}
              src={thumbUrl}
            />
          </div>
          <div className="provider-details">
            <div className="provider-header">
              <Icon svg={providerInfo.icon} />
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
                  ` avec les données ${providerInfo.name} tous les soirs. De ce fait, seuls sa description et son titre sont modifiables,` +
                  " pour vos besoins d'éditorialisation pour le pass Culture."}
              </p>
            </div>
          </div>
        </div>
      </Fragment>
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
