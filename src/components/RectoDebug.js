import React from 'react'

const RectoDebug = ({ chosenOffer,
  dateRead,
  id,
  contentLength,
  index
}) => {
  return (
    <div className='recto-debug absolute left-0 ml2 p2'>
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

export default RectoDebug
