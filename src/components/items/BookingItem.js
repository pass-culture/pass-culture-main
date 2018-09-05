import React from 'react'
import PropTypes from 'prop-types'

import { Icon } from 'pass-culture-shared'

const statePictoMap = {
  payement: 'picto-validation',
  validation: 'picto-encours-S',
  pending: 'picto-temps-S',
  error: 'picto-echec',
}

const BookingItem = ({ booking }) => (
  <React.Fragment>
    <tr className="offer-item">
      <td colSpan="5" className="title">
        Atelier BD et lecture avec Joan sfar
      </td>
      <td rowSpan="2">27/04/2018</td>
      <td rowSpan="2">5/10</td>
      <td rowSpan="2">5&euro;</td>
      <td rowSpan="2">4&euro;</td>
      <td rowSpan="2">
        <Icon svg={statePictoMap['payement']} className="picto tiny" /> Réglé
      </td>
      <td rowSpan="2">
        <button
          className="actionButton"
          type="button"
          onClick={() => {
            if (window.confirm('Annuler cette réservation ?')) {
              console.log('ok')
            } else {
              console.log('ko')
            }
          }}
        />
      </td>
    </tr>
    <tr className="offer-item first-col">
      <td>24/04/2018</td>
      <td>DÉDICACE</td>
      <td>Structure</td>
      <td>Folies d'encre</td>
      <td>
        {/*<Icon svg="picto-user" />*/}
        <Icon svg="picto-group" /> 5
      </td>
    </tr>
  </React.Fragment>
)

BookingItem.propTypes = {
  booking: PropTypes.object.isRequired,
}

export default BookingItem
