import classnames from 'classnames'
import React from 'react'

const Clue = ({ content,
  item
}) => {
  return (
    <div className={classnames('clue absolute', { 'clue--hidden': item !== 0 })}>
      {content.id}
    </div>
  )
}

export default Clue
