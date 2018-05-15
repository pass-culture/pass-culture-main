import React from 'react'
import capitalize from '../../utils/capitalize'

export default ({children}) => {
  return <span>{React.Children.map(children, c => (typeof c === 'string' ? capitalize(c) : c))}</span>
}
