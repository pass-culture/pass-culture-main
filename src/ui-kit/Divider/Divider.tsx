import classnames from 'classnames'
import React, { FC } from 'react'
import styles from './Divider.module.scss'

type Size = 'medium'; 
interface IDividerProps {
  size?: Size;
  className?: string;
}
const Divider: FC<IDividerProps> = ({ size, className }) => {
    const sizeClassName = {
      medium: styles['divider-medium']
    }[size || 'medium'] 
   return (
     <div className={classnames(styles.divider, sizeClassName, className )} />
   )
}
export default Divider