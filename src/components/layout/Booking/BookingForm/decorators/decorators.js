import createDecorator from 'final-form-calculate'
import onCalendarUpdates from './utils/onCalendarUpdates'
import onTimeUpdates from './utils/onTimeUpdates'

const decorators = [
  createDecorator(
    { field: 'date', updates: onCalendarUpdates },
    { field: 'time', updates: onTimeUpdates }
  ),
]

export default decorators
