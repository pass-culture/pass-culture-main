import * as reactIconPack from 'react-icons/lib/md';
import React from 'react'

export default ( props ) => {
  const { svg, ...imgProps } = props;
  if (svg) {
    return <img src={`/icons/${svg}.svg`} alt={svg} {...imgProps} />
  } else {
    const iconName = 'Md' + props.name.replace(/(^|-)(\w)/g, (m0, m1, m2) => m2.toUpperCase());
    return reactIconPack[iconName]();
  }

}
