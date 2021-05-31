import EventStocks from './EventStocks'
import ThingStocks from './ThingStocks'

export default props => {
  return props.offer.isEvent ? EventStocks(props) : ThingStocks(props)
}
