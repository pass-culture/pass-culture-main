import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import { NavLink, matchPath } from 'react-router-dom'

const noop = () => {}

const renderLinkContent = (icon, title, styles) => (
  <React.Fragment>
    <span
      style={styles}
      className="flex-0 text-center menu-icon mr16 text-center"
    >
      <Icon svg={`ico-${icon}`} alt="" />
    </span>
    <span className="flex-1 is-medium">
      {title}
    </span>
  </React.Fragment>
)

class MenuItemContent extends React.PureComponent {
  renderNavLink = opts => {
    const { clickHandler, item, location } = this.props
    const { title, disabled, icon, path } = item
    const currentpath = location.pathname
    const isactive = matchPath(currentpath, item)
    const pathto = isactive ? currentpath : path
    return (
      <NavLink
        key={path}
        to={pathto}
        disabled={disabled}
        onClick={clickHandler}
        activeClassName={opts.activeClass}
        className={`navlink mx12 flex-columns ${opts.cssclass}`}
      >
        {renderLinkContent(icon, title)}
      </NavLink>
    )
  }

  renderSimpleLink = opts => {
    const { clickHandler, item } = this.props
    const { title, icon, disabled, href } = item
    return (
      <a
        key={href}
        href={href}
        disabled={disabled}
        onClick={clickHandler}
        className={`navlink mx12 flex-columns ${opts.cssclass}`}
      >
        {renderLinkContent(icon, title)}
      </a>
    )
  }

  render() {
    const { item, location } = this.props
    // regle stricte
    // si on est sur la page verso d'une offre
    // aucun menu n'est actif
    // TODO: replace with https://reacttraining.com/react-router/web/api/NavLink/location-object
    const isverso =
      location.search && location.search.indexOf('?to=verso') !== -1
    const activeClass = isverso ? null : 'active'
    const cssclass = (item.disabled && 'is-disabled') || ''
    const options = { activeClass, cssclass }
    if (item.href) return this.renderSimpleLink(options)
    return this.renderNavLink(options)
  }
}

MenuItemContent.defaultProps = {
  clickHandler: noop,
}

MenuItemContent.propTypes = {
  clickHandler: PropTypes.func,
  item: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
}

export default MenuItemContent
