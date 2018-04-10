import React from 'react'

const RectoDebug = ({ contentLength,
  index,
  offer,
  userMediation,
}) => {
  return (
    <div className='recto-debug absolute left-0 ml2 p2'>
      <span>
        {userMediation && userMediation.id} {offer && offer.id} {index + 1}
      </span>
      {
        userMediation && userMediation.dateRead && [
          <span key={0}>
            &middot;
          </span>,
          <span key={1}>
            {userMediation.dateRead}
          </span>
        ]
      }
    </div>
  )
}

export default RectoDebug
