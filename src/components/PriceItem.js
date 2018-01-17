import React, { Component } from 'react'
import moment from 'moment'

const FormItem = ({ name, value }) => (
  <div className='flex items-center justify-center'>
    <label className='mr2 right-align'>
      {name}
    </label>
    <div className='price-item__value'>
      {value}
    </div>
  </div>
)

class PriceItem extends Component {
  handleFormatDate = ({ endDate, startDate }) => {
    this.setState({
      formatEndDate: moment(endDate).format('YYYY-MM-DD'),
      formatStartDate: moment(startDate).format('YYYY-MM-DD')
    })
  }
  componentWillMount () {
    this.handleFormatDate(this.props)
  }
  componentWillReceiveProps (nextProps) {
    const { endDate, startDate } = nextProps
    // we just avoid here to recompute the date at each render
    if (endDate !== this.props.endDate || startDate !== this.props.startDate) {
      this.handleFormatDate(nextProps)
    }
  }
  render () {
    const { size, value } = this.props
    const { formatEndDate, formatStartDate } = this.state
    return (
      <div className='price-item mb3 col-9 mx-auto p2'>

        <FormItem name='début' value={formatStartDate} />
        <br />

        <FormItem name='fin' value={formatEndDate} />
        <br />

        <FormItem name='groupe' value={size} />
        <br />

        <FormItem name='prix' value={value} />
      </div>
    )
  }
}

export default PriceItem
