import React from 'react'

const RectoDebug = ({ contentLength, index, offer, recommendation }) => {
  return (
    <div className="recto-debug absolute right-0 mr2 p2">
      <span>
        {recommendation && recommendation.id} {offer && offer.id} {index + 1}
      </span>
      {recommendation &&
        recommendation.dateRead && [
          <span key={0}>&middot;</span>,
          <span key={1}>{recommendation.dateRead}</span>,
        ]}
    </div>
  )
}

export default RectoDebug
