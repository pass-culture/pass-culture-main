import{i as e}from"./chunk-DseTPa7n.js";import{r as t}from"./iframe-COrE2XJm.js";import{t as n}from"./jsx-runtime-BuabnPLX.js";import{t as r}from"./SvgIcon-DK-x56iF.js";import{t as i}from"./TextInput-BD95hSoy.js";import{n as a,r as o,t as s}from"./iconsList-DsXSjL2h.js";import{t as c}from"./stroke-search-DVpFKH3D.js";var l=e(t(),1),u=`_title_1490c_1`,d=`_container_1490c_28`,f=`_name_1490c_41`,p=`_icon_1490c_7`,m={title:u,"icon-stories":`_icon-stories_1490c_7`,"icon-list":`_icon-list_1490c_13`,"search-input-container":`_search-input-container_1490c_21`,container:d,name:f,"name-container":`_name-container_1490c_44`,"copy-to-clipboard":`_copy-to-clipboard_1490c_48`,"icon-container":`_icon-container_1490c_51`,"copy-to-clipboard-wrapper":`_copy-to-clipboard-wrapper_1490c_59`,icon:p},h=n(),g=(e,t)=>(e=`.*`+e.toLowerCase().split(``).join(`.*`)+`.*`,new RegExp(e).test(t.toLowerCase())),_=[{title:`Full icons`,icons:s},{title:`Stroke icons`,icons:o},{title:`Other icons`,icons:a}],v=()=>{let[e,t]=(0,l.useState)(``),n=async e=>{e.persist();let t=e.currentTarget;await navigator.clipboard.writeText(t.getAttribute(`data-src`)??``),t.classList.add(m[`copy-to-clipboard`]);let n=setTimeout(()=>{t.classList.remove(m[`copy-to-clipboard`]),clearTimeout(n)},600)};return(0,h.jsxs)(`div`,{className:m[`icon-stories`],children:[(0,h.jsx)(`div`,{className:m[`search-input-container`],children:(0,h.jsx)(i,{name:`search`,label:`Rechercher une icon`,icon:c,onChange:e=>t(e.target.value),value:e})}),_.map(t=>{let i=t.icons.filter(t=>g(e,t.src));return i.length===0?null:(0,h.jsxs)(`div`,{children:[(0,h.jsx)(`h1`,{className:m.title,children:t.title}),(0,h.jsx)(`div`,{className:m[`icon-list`],children:i.map(e=>{let t=e.src.split(`/`),i=t[t.length-1].split(`.`)[0].replace(`full-`,``).replace(`stroke-`,``).replace(`shadow-`,``);return(0,h.jsxs)(`div`,{className:m.container,onClick:n,"data-src":e.src,children:[(0,h.jsx)(`div`,{className:m[`copy-to-clipboard-wrapper`],children:(0,h.jsx)(`span`,{children:`Copié !`})}),(0,h.jsx)(`div`,{className:m[`icon-container`],children:(0,h.jsx)(r,{src:e.src,alt:e.src,viewBox:e.viewBox,className:m.icon})}),(0,h.jsx)(`div`,{className:m[`name-container`],children:(0,h.jsx)(`span`,{className:m.name,children:i})})]},e.src)})})]},t.title)})]})},y={title:`@/icons/Icons`};v.parameters={...v.parameters,docs:{...v.parameters?.docs,source:{originalSource:`() => {
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
}`,...v.parameters?.docs?.source}}};var b=[`Icons`];export{v as Icons,b as __namedExportsOrder,y as default};