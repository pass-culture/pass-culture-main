import { useEffect, useRef } from 'react'
import ReactDOM from 'react-dom'

// https://fr.reactjs.org/docs/portals.html
const PortalContainer = ({ children }) => {
  const containerRef = useRef(null)
  if (containerRef.current === null) containerRef.current = document.createElement('div')

  useEffect(() => {
    const portalsRoot = document.getElementById('portals-root') || createPortalsRoot()
    portalsRoot.appendChild(containerRef.current)

    return () => portalsRoot.removeChild(containerRef.current)
  }, [])

  return ReactDOM.createPortal(children, containerRef.current)
}

// https://github.com/testing-library/react-testing-library/issues/62#issuecomment-438653348
function createPortalsRoot() {
  const portalsRoot = document.createElement('div')
  portalsRoot.setAttribute('id', 'portals-root')
  document.body.appendChild(portalsRoot)

  return portalsRoot
}

export default PortalContainer
