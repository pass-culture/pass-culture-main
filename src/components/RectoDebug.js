import React from 'react'

const RectoDebug = ({ contentLength,
  index,
  currentOffer,
  currentUserMediation,
}) => {
  return (
    <div className='recto-debug absolute left-0 ml2 p2'>
      <span>
        {currentUserMediation.id} {currentOffer.id} {index + 1}/{contentLength}
      </span>
      {
        currentUserMediation.dateRead && [
          <span key={0}>
            &middot;
          </span>,
          <span key={1}>
            {currentUserMediation.dateRead}
          </span>
        ]
      }
    </div>
  )
}

export default RectoDebug
