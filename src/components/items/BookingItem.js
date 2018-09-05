import React from 'react'
import PropTypes from 'prop-types'

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
      <td rowSpan="2">Réglé</td>
      <td rowSpan="2">
        <button
          type="button"
          onClick={() => {
            if (window.confirm('Annuler cette réservation ?')) {
              console.log('ok')
            } else {
              console.log('ko')
            }
          }}>
          Annuler
        </button>
      </td>
    </tr>
    <tr className="offer-item first-col">
      <td>24/04/2018</td>
      <td>DÉDICACE</td>
      <td>Structure</td>
      <td>Folies d'encre</td>
      <td>Type</td>
    </tr>
  </React.Fragment>
)

BookingItem.propTypes = {
  booking: PropTypes.object.isRequired,
}

export default BookingItem
