import classnames from 'classnames'
import React from 'react'

const Clue = ({ dateRead,
  id,
  contentLength,
  index,
  item
}) => {
  return (
    <div className={classnames('clue absolute', { 'clue--hidden': item !== 0 })}>
      {id} {index}/{contentLength} <br/>
      {dateRead}
    </div>
  )
}

export default Clue
