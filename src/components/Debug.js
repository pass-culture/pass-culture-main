import React from 'react'

const Debug = ({ chosenOffer,
  dateRead,
  id,
  contentLength,
  index
}) => {
  return (
    <div className='debug absolute left-0 top-0 ml2 mt2 p2'>
      <span>
        {id} {chosenOffer.id} {index}/{contentLength}
      </span>
      {
        dateRead && [
          <span key={0}>
            &middot;
          </span>,
          <span key={1}>
            {dateRead}
          </span>
        ]
      }
    </div>
  )
}

export default Debug
