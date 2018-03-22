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
        <span className='clue__sep'>
          &middot;
        </span>
        <span>
          100m
        </span>
        <span className='clue__sep'>
          &middot;
        </span>
        <span>
          {id} {index}/{contentLength}
        </span>
        {
          dateRead && [
            <span className='clue__sep' key={0}>
              &middot;
            </span>,
            <span key={1}>
              {dateRead}
            </span>
          ]
        }
      </div>
    </div>
  )
}

export default Clue
