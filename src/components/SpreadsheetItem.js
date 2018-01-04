import React from 'react'

const SpreadsheetItem = ({ style,
  title,
  thumbnailUrl
}) => {
  const { imgStyle } = style
  return (
    <div style={style}>
      <img alt='thumbnail' src={thumbnailUrl} style={imgStyle} />
      {title}
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
