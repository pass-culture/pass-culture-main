import React from 'react'

const StyleguideTitle = ({ className, componentName }) => {
  return (
    <div>
      <hr className="separator" />
      <h2 id={className}>
        {componentName}
      </h2>
    </div>
  )
}

export default StyleguideTitle
