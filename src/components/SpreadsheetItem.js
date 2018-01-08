import React from 'react'

const SpreadsheetItem = ({ name,
  style,
  work: { thumbnailUrl }
}) => {
  const { imgStyle } = style
  return (
    <div style={style}>
      <img alt='thumbnail' src={thumbnailUrl} style={imgStyle} />
      {name}
    </div>
  )
}

SpreadsheetItem.defaultProps = {
  style: { alignItems: 'center',
    display: 'flex',
    imgStyle: {
      height: '5rem',
      width: '5rem'
    }
  }
}

export default SpreadsheetItem
