import React, { Component } from 'react'
import { rgb_to_hsv } from 'colorsys'

class OfferInfo extends Component {

  constructor () {
    super ()
    this.state = {
      headerStyle: {},
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.firstThumbDominantColor !== nextProps.firstThumbDominantColor) {
      this.setHeaderStyle(nextProps.firstThumbDominantColor);
    }
  }

  setHeaderStyle(color) {
    if (color) {
      const [red, green, blue] = color;
      const {h} = rgb_to_hsv(red, green, blue);
      this.setState({
        headerStyle: {backgroundColor: `hsl(${h}, 100%, 15%)`}
      });
    }
  }

  render() {
    const {
      // description,
      eventOccurence,
      // id,
      occurencesAtVenue,
      // price,
      // sellersFavorites,
      thing,
      // thingOrEventOccurence,
      thumbUrl,
      venue,
      children,
    } = this.props;

    return (
      <div className='offer-info'>
        <div className='verso-header' style={this.state.headerStyle}>
          <h2> { thing.name }, de { thing.extraData.author } </h2>
          <h6> {venue.name} </h6>
        </div>
        {children}
        <div className='content'>
          <img alt='' className='offerPicture' src={thumbUrl} />
          {thing.description && (
            <div className='description'>
              { thing.description.split('\n').map((p, index) => <p key={index}>{p}</p>) }
            </div>
          )}
          {eventOccurence && (
            <div>
              <h3>Quoi ?</h3>
              <p>{eventOccurence.event.description}</p>
            </div>
          )}
          {occurencesAtVenue && (
            <div>
              <h3>Quand ?</h3>
              <ul className='dates-info'>
                { occurencesAtVenue.map((occurence, index) => (
                  <li key={index}>
                    <span> { occurence.beginningDatetime } </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {venue.address && (
            <div>
              <h3>Où ?</h3>
              <ul className='address-info'>
                <li>{venue.name}</li>
                {venue.address.split(/[,\n\r]/).map((el, index) => (<li key={index}>{el}</li>))}
              </ul>
            </div>
          )}
          <p>
          </p>
        </div>
      </div>
    )
  }
}

export default OfferInfo
