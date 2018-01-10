import React, { Component } from 'react'
import { connect } from 'react-redux'

import { showModal } from '../reducers/modal'

class OfferItem extends Component {
  onDeleteClick = () => {
    this.props.showModal(<div> Hello </div>)
  }
  onEditClick = () => {
    this.props.showModal(<div> Hello </div>)
  }
  render () {
    const { name,
      // style,
      work: { thumbnailUrl }
    } = this.props
    // const { imgStyle } = style
    return (
      <div className='offer-item flex items-center justify-between mb1 p1'
      >
        <img alt='thumbnail'
          className='offer-item__image mr2'
          src={thumbnailUrl}
        />
        {name}
        <div className='offer-item__space flex-auto' />
        <button className='button button--alive'
          onClick={this.onEditClick}
        >
          Edit
        </button>
        <button className='button button--alive'
          onClick={this.onDeleteClick}
        >
          Delete
        </button>
      </div>
    )
  }
}

OfferItem.defaultProps = {
  /*
  style: { alignItems: 'center',
    display: 'flex',
    imgStyle: {
      height: '5rem',
      width: '5rem'
    },
    width: '20rem'
  }
  */
}

export default connect(null, { showModal })(OfferItem)
