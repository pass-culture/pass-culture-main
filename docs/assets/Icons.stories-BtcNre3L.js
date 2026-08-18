import{n as e}from"./rolldown-runtime-DkW27tQK.js";import{d as t}from"./iframe-BJ1J-89Y.js";import{t as n}from"./jsx-runtime-DeHZSEgm.js";import{n as r,t as i}from"./SvgIcon-DRPrlrFF.js";import{n as a,t as o}from"./TextInput-Ce44B4DB.js";import{i as s,n as c,r as l,t as u}from"./iconsList-fouh3l9Q.js";import{n as d,t as f}from"./stroke-search-Dn4g4af-.js";var p,m,h,g,_;function v(){return(v=e((()=>{p=`_title_1490c_1`,m=`_container_1490c_28`,h=`_name_1490c_41`,g=`_icon_1490c_7`,_={title:p,"icon-stories":`_icon-stories_1490c_7`,"icon-list":`_icon-list_1490c_13`,"search-input-container":`_search-input-container_1490c_21`,container:m,name:h,"name-container":`_name-container_1490c_44`,"copy-to-clipboard":`_copy-to-clipboard_1490c_48`,"icon-container":`_icon-container_1490c_51`,"copy-to-clipboard-wrapper":`_copy-to-clipboard-wrapper_1490c_59`,icon:g}})))()}var y,b,x,S,C,w;function T(){return(T=e((()=>{y=t(),r(),f(),v(),c(),a(),b=n(),x=[{title:`Full icons`,icons:u},{title:`Stroke icons`,icons:s},{title:`Other icons`,icons:l}],S=()=>{let[e,t]=(0,y.useState)(``),n=async e=>{e.persist();let t=e.currentTarget;await navigator.clipboard.writeText(t.getAttribute(`data-src`)??``),t.classList.add(_[`copy-to-clipboard`]);let n=setTimeout(()=>{t.classList.remove(_[`copy-to-clipboard`]),clearTimeout(n)},600)};return(0,b.jsxs)(`div`,{className:_[`icon-stories`],children:[(0,b.jsx)(`div`,{className:_[`search-input-container`],children:(0,b.jsx)(o,{name:`search`,label:`Rechercher une icon`,icon:d,onChange:e=>t(e.target.value),value:e})}),x.map(t=>{let r=t.icons.filter(t=>t.src.toLowerCase().includes(e.toLowerCase()));return r.length===0?null:(0,b.jsxs)(`div`,{children:[(0,b.jsx)(`h1`,{className:_.title,children:t.title}),(0,b.jsx)(`div`,{className:_[`icon-list`],children:r.map(e=>{let t=e.src.split(`/`),r=t[t.length-1].split(`.`)[0].replace(`full-`,``).replace(`stroke-`,``).replace(`shadow-`,``);return(0,b.jsxs)(`div`,{className:_.container,onClick:n,"data-src":e.src,children:[(0,b.jsx)(`div`,{className:_[`copy-to-clipboard-wrapper`],children:(0,b.jsx)(`span`,{children:`Copié !`})}),(0,b.jsx)(`div`,{className:_[`icon-container`],children:(0,b.jsx)(i,{src:e.src,alt:e.src,viewBox:e.viewBox,className:_.icon})}),(0,b.jsx)(`div`,{className:_[`name-container`],children:(0,b.jsx)(`span`,{className:_.name,children:r})})]},e.src)})})]},t.title)})]})},C={title:`@/icons/Icons`},S.parameters={...S.parameters,docs:{...S.parameters?.docs,source:{originalSource:`() => {
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
      const filteredIcons = section.icons.filter(iconListItem => iconListItem.src.toLowerCase().includes(searchInput.toLowerCase()));
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
}`,...S.parameters?.docs?.source}}},w=[`Icons`]})))()}T();export{S as Icons,w as __namedExportsOrder,C as default};