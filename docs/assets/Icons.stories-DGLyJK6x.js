import{i as e}from"./chunk-DseTPa7n.js";import{t}from"./react-DCnNfEIY.js";import{t as n}from"./jsx-runtime-BUC2lftT.js";import{t as r}from"./SvgIcon-zPyG_A85.js";import{t as i}from"./TextInput-fUX_gKye.js";import{n as a,r as o,t as s}from"./iconsList-W2PFxqtq.js";import{t as c}from"./stroke-search-BjINRfAN.js";var l=e(t(),1),u={title:`_title_1490c_1`,"icon-stories":`_icon-stories_1490c_7`,"icon-list":`_icon-list_1490c_13`,"search-input-container":`_search-input-container_1490c_21`,container:`_container_1490c_28`,name:`_name_1490c_41`,"name-container":`_name-container_1490c_44`,"copy-to-clipboard":`_copy-to-clipboard_1490c_48`,"icon-container":`_icon-container_1490c_51`,"copy-to-clipboard-wrapper":`_copy-to-clipboard-wrapper_1490c_59`,icon:`_icon_1490c_7`},d=n(),f=(e,t)=>(e=`.*`+e.toLowerCase().split(``).join(`.*`)+`.*`,new RegExp(e).test(t.toLowerCase())),p=[{title:`Full icons`,icons:s},{title:`Stroke icons`,icons:o},{title:`Other icons`,icons:a}],m=()=>{let[e,t]=(0,l.useState)(``),n=async e=>{e.persist();let t=e.currentTarget;await navigator.clipboard.writeText(t.getAttribute(`data-src`)??``),t.classList.add(u[`copy-to-clipboard`]);let n=setTimeout(()=>{t.classList.remove(u[`copy-to-clipboard`]),clearTimeout(n)},600)};return(0,d.jsxs)(`div`,{className:u[`icon-stories`],children:[(0,d.jsx)(`div`,{className:u[`search-input-container`],children:(0,d.jsx)(i,{name:`search`,label:`Rechercher une icon`,icon:c,onChange:e=>t(e.target.value),value:e})}),p.map(t=>{let i=t.icons.filter(t=>f(e,t.src));return i.length===0?null:(0,d.jsxs)(`div`,{children:[(0,d.jsx)(`h1`,{className:u.title,children:t.title}),(0,d.jsx)(`div`,{className:u[`icon-list`],children:i.map(e=>{let t=e.src.split(`/`),i=t[t.length-1].split(`.`)[0].replace(`full-`,``).replace(`stroke-`,``).replace(`shadow-`,``);return(0,d.jsxs)(`div`,{className:u.container,onClick:n,"data-src":e.src,children:[(0,d.jsx)(`div`,{className:u[`copy-to-clipboard-wrapper`],children:(0,d.jsx)(`span`,{children:`Copié !`})}),(0,d.jsx)(`div`,{className:u[`icon-container`],children:(0,d.jsx)(r,{src:e.src,alt:e.src,viewBox:e.viewBox,className:u.icon})}),(0,d.jsx)(`div`,{className:u[`name-container`],children:(0,d.jsx)(`span`,{className:u.name,children:i})})]},e.src)})})]},t.title)})]})},h={title:`@/icons/Icons`};m.parameters={...m.parameters,docs:{...m.parameters?.docs,source:{originalSource:`() => {
  const [searchInput, setSearchInput] = useState('');
  const onClick = async (e: React.MouseEvent<HTMLDivElement>) => {
    e.persist();
    const target = e.currentTarget as Element;
    await navigator.clipboard.writeText(target.getAttribute('data-src') ?? '');
    target.classList.add(styles['copy-to-clipboard']);
    const timeoutId = setTimeout(() => {
      target.classList.remove(styles['copy-to-clipboard']);
      clearTimeout(timeoutId);
    }, 600);
  };
  return <div className={styles['icon-stories']}>
      <div className={styles['search-input-container']}>
        <TextInput name="search" label='Rechercher une icon' icon={strokeSearchIcon} onChange={event => setSearchInput(event.target.value)} value={searchInput} />
      </div>

      {iconsSections.map(section => {
      const filteredIcons = section.icons.filter(iconListItem => fuzzyMatch(searchInput, iconListItem.src));
      if (filteredIcons.length === 0) {
        return null;
      }
      return <div key={section.title}>
            <h1 className={styles['title']}>{section.title}</h1>

            <div className={styles['icon-list']}>
              {filteredIcons.map(icon => {
            const fileNameParts = icon.src.split('/');
            const iconName = fileNameParts[fileNameParts.length - 1].split('.')[0].replace('full-', '').replace('stroke-', '').replace('shadow-', '');
            return <div key={icon.src} className={styles['container']} onClick={onClick} data-src={icon.src}>
                    <div className={styles['copy-to-clipboard-wrapper']}>
                      <span>
                        Copié !
                      </span>
                    </div>

                    <div className={styles['icon-container']}>
                      <SvgIcon src={icon.src} alt={icon.src} viewBox={icon.viewBox} className={styles['icon']} />
                    </div>

                    <div className={styles['name-container']}>
                      <span className={styles['name']}>{iconName}</span>
                    </div>
                  </div>;
          })}
            </div>
          </div>;
    })}
    </div>;
}`,...m.parameters?.docs?.source}}};var g=[`Icons`];export{m as Icons,g as __namedExportsOrder,h as default};