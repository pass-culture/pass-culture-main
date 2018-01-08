import React, { Component } from 'react'
import { connect } from 'react-redux'

import Button from './Button'
import { showModal } from '../reducers/modal'

class OfferItem extends Component {
  constructor () {
    super()
    this.onEditClick = this._onEditClick.bind(this)
  }
  _onEditClick ()  {
    this.props.showModal(<div> Hello </div>)
  }
  render () {
    const { name,
      style,
      work: { thumbnailUrl }
    } = this.props
    const { imgStyle } = style
    return (
      <div className='offer-item flex items-center justify-between mb1 p1'
        style={style}
        style={null}
      >
        <img alt='thumbnail'
          className='offer-item__image'
          src={thumbnailUrl}
          style={imgStyle}
          style={null}
        />
        {name}
        <Button className='button button--alive'
          onClick={this.onEditClick}
        >
          Edit
        </Button>
      </div>
    )
  }
}

OfferItem.defaultProps = {
  style: { alignItems: 'center',
    display: 'flex',
    imgStyle: {
      height: '5rem',
      width: '5rem'
    },
    width: '20rem'
  }
}

export default connect(null, { showModal })(OfferItem)
