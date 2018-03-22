import classnames from 'classnames'
import React from 'react'

const Clue = ({ chosenOffer,
  dateRead,
  id,
  contentLength,
  index,
  item
}) => {
  return (
    <div className={classnames('clue', { 'clue--hidden': item !== 0 })}>
      <div>
        <span>
          { ("" + chosenOffer.price).replace('.', ',') }&nbsp;€
        </span>
        <span style={{fontFamily: 'sans'}}>
          &middot;
        </span>
        <span>
          100m
        </span>
      </div>
      {id} {index}/{contentLength} <br/>
      {dateRead}
    </div>
  )
}

export default Clue
