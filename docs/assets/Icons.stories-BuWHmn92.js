import{i as e,s as t}from"./preload-helper-xPQekRTU.js";import{C as n}from"./iframe-D-ws3S7b.js";import{t as r}from"./jsx-runtime-CaZkqeYb.js";import{n as i,t as a}from"./SvgIcon-DVxB_oBw.js";import{n as o,t as s}from"./TextInput-Db2jZRM_.js";import{i as c,n as l,r as u,t as d}from"./iconsList-wRjicZAg.js";import{n as f,t as p}from"./stroke-search-hvN1lQvr.js";var m,h,g,_,v,y=e((()=>{m=`_title_1490c_1`,h=`_container_1490c_28`,g=`_name_1490c_41`,_=`_icon_1490c_7`,v={title:m,"icon-stories":`_icon-stories_1490c_7`,"icon-list":`_icon-list_1490c_13`,"search-input-container":`_search-input-container_1490c_21`,container:h,name:g,"name-container":`_name-container_1490c_44`,"copy-to-clipboard":`_copy-to-clipboard_1490c_48`,"icon-container":`_icon-container_1490c_51`,"copy-to-clipboard-wrapper":`_copy-to-clipboard-wrapper_1490c_59`,icon:_}})),b,x,S,C,w,T;e((()=>{b=t(n(),1),i(),p(),y(),l(),o(),x=r(),S=[{title:`Full icons`,icons:d},{title:`Stroke icons`,icons:c},{title:`Other icons`,icons:u}],C=()=>{let[e,t]=(0,b.useState)(``),n=async e=>{e.persist();let t=e.currentTarget;await navigator.clipboard.writeText(t.getAttribute(`data-src`)??``),t.classList.add(v[`copy-to-clipboard`]);let n=setTimeout(()=>{t.classList.remove(v[`copy-to-clipboard`]),clearTimeout(n)},600)};return(0,x.jsxs)(`div`,{className:v[`icon-stories`],children:[(0,x.jsx)(`div`,{className:v[`search-input-container`],children:(0,x.jsx)(s,{name:`search`,label:`Rechercher une icon`,icon:f,onChange:e=>t(e.target.value),value:e})}),S.map(t=>{let r=t.icons.filter(t=>t.src.toLowerCase().includes(e.toLowerCase()));return r.length===0?null:(0,x.jsxs)(`div`,{children:[(0,x.jsx)(`h1`,{className:v.title,children:t.title}),(0,x.jsx)(`div`,{className:v[`icon-list`],children:r.map(e=>{let t=e.src.split(`/`),r=t[t.length-1].split(`.`)[0].replace(`full-`,``).replace(`stroke-`,``).replace(`shadow-`,``);return(0,x.jsxs)(`div`,{className:v.container,onClick:n,"data-src":e.src,children:[(0,x.jsx)(`div`,{className:v[`copy-to-clipboard-wrapper`],children:(0,x.jsx)(`span`,{children:`Copié !`})}),(0,x.jsx)(`div`,{className:v[`icon-container`],children:(0,x.jsx)(a,{src:e.src,alt:e.src,viewBox:e.viewBox,className:v.icon})}),(0,x.jsx)(`div`,{className:v[`name-container`],children:(0,x.jsx)(`span`,{className:v.name,children:r})})]},e.src)})})]},t.title)})]})},w={title:`@/icons/Icons`},C.parameters={...C.parameters,docs:{...C.parameters?.docs,source:{originalSource:`() => {
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
}`,...C.parameters?.docs?.source}}},T=[`Icons`]}))();export{C as Icons,T as __namedExportsOrder,w as default};