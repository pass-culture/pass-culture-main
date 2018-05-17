import React from 'react'

const Debug = ({log}) => {
  return (
    <div className='debug-modal'>
      <h1 className='title'>Debug</h1>
      <pre>{log}</pre>
    </div>
  )
}

export default Debug
