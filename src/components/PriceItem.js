import React, { Component } from 'react'
import moment from 'moment'

class PriceItem extends Component {
  handleFormatDate = ({ endDate, startDate }) => {
    this.setState({
      formatEndDate: moment(endDate).format('YYYY-MM-DD'),
      formatStartDate: moment(startDate).format('YYYY-MM-DD'),
    })
  }
  componentWillMount() {
    this.handleFormatDate(this.props)
  }
  componentWillReceiveProps(nextProps) {
    const { endDate, startDate } = nextProps
    // we just avoid here to recompute the date at each render
    if (endDate !== this.props.endDate || startDate !== this.props.startDate) {
      this.handleFormatDate(nextProps)
    }
  }
  render() {
    const { groupSize, value } = this.props
    // const { formatEndDate, formatStartDate } = this.state
    return (
      <div className="price-item flex items-center p1">
        {groupSize > 1 && <div className="mr1">BP</div>}
        <div>
          <span className="h3"> {value} </span> €{' '}
          {groupSize > 1 && (
            <span>
              {' '}
              à partir de <span className="h3"> {groupSize} </span> pers.{' '}
            </span>
          )}
        </div>
        {/*
          <div className='price-item__date'>
            {formatStartDate} / {formatEndDate}
          </div>
          */}
      </div>
    )
  }
}

export default PriceItem
