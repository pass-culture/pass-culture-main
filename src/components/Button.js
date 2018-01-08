import React from 'react'

const Button = ({ children,
  className,
  extraClass,
  onClick
}) => {
  return (
    <button className={className || 'button'} onClick={onClick}>
      {children}
    </button>
  )
}

export default Button
