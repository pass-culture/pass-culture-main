---
to: <%= absPath %>/<%= component_name %>.tsx
---
<%
 InterfaceComponentName = `I${ComponentName}Props`
%>// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React from 'react'
<% if (includeScss) { %>
import styles from './styles.module.scss'
<% } %>
interface <%= InterfaceComponentName %> {}

const <%= ComponentName %> = (props: <%= InterfaceComponentName %>): JSX.Element => {
  return <div className={styles["<%= cssClassName %>"]} data-testid="<%= testId %>" />
}

export default <%= ComponentName %>
