import{j as t}from"./jsx-runtime-C_uOM0Gm.js";import{r as m}from"./iframe-CTnXOULQ.js";import{S as d}from"./SvgIcon-CJiY4LCz.js";import{s as u}from"./stroke-search-Bph5aoaJ.js";import{f as h,s as v,o as _}from"./iconsList-DgqnJnmb.js";import{T as y}from"./TextInput-DOsfrCQI.js";import"./preload-helper-PPVm8Dsz.js";import"./full-back-DIKqgBhG.js";import"./full-thumb-up-Bb4kpRpM.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-BZV8LNX-.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-help-blUMxBcv.js";import"./full-show-BUp4jmvL.js";import"./full-info-D24AtBVt.js";import"./full-three-dots-DhyQI2cN.js";import"./full-link-CYVo23DH.js";import"./full-location-CVEaH-Cp.js";import"./full-more-DLJb58kc.js";import"./full-next-B_76kGmE.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-trash-CEfIUI4M.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-pass-CALgybTM.js";import"./stroke-picture-VF2OicDu.js";import"./stroke-thing-O6UIROL8.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-user-u-f9pznf.js";import"./stroke-video-Cd5kQZzx.js";import"./stroke-wrong-BAouvvNg.js";import"./index-TscbDd2H.js";import"./FieldFooter-CL0tzobd.js";import"./index.module-DEHgy3-r.js";import"./FieldHeader-DxZ9joXq.js";import"./Tooltip-GJ5PEk5n.js";const b="_title_1nb02_1",I="_container_1nb02_34",N="_name_1nb02_47",x="_icon_1nb02_7",e={title:b,"icon-stories":"_icon-stories_1nb02_7","icon-list":"_icon-list_1nb02_13","search-input-container":"_search-input-container_1nb02_21",container:I,name:N,"name-container":"_name-container_1nb02_50","copy-to-clipboard":"_copy-to-clipboard_1nb02_54","icon-container":"_icon-container_1nb02_57","copy-to-clipboard-wrapper":"_copy-to-clipboard-wrapper_1nb02_65",icon:x},f=(i,n)=>(i=".*"+i.toLowerCase().split("").join(".*")+".*",new RegExp(i).test(n.toLowerCase())),g=[{title:"Full icons",icons:h},{title:"Stroke icons",icons:v},{title:"Other icons",icons:_}],c=()=>{const[i,n]=m.useState(""),a=async o=>{o.persist();const r=o.currentTarget;await navigator.clipboard.writeText(r.getAttribute("data-src")??""),r.classList.add(e["copy-to-clipboard"]);const s=setTimeout(()=>{r.classList.remove(e["copy-to-clipboard"]),clearTimeout(s)},600)};return t.jsxs("div",{className:e["icon-stories"],children:[t.jsx("div",{className:e["search-input-container"],children:t.jsx(y,{name:"search",label:"Rechercher une icon",icon:u,onChange:o=>n(o.target.value),value:i})}),g.map(o=>{const r=o.icons.filter(s=>f(i,s.src));return r.length===0?null:t.jsxs("div",{children:[t.jsx("h1",{className:e.title,children:o.title}),t.jsx("div",{className:e["icon-list"],children:r.map(s=>{const l=s.src.split("/"),p=l[l.length-1].split(".")[0].replace("full-","").replace("stroke-","").replace("shadow-","");return t.jsxs("div",{className:e.container,onClick:a,"data-src":s.src,children:[t.jsx("div",{className:e["copy-to-clipboard-wrapper"],children:t.jsx("span",{className:e["copy-to-clipboard-name"],children:"Copié !"})}),t.jsx("div",{className:e["icon-container"],children:t.jsx(d,{src:s.src,alt:s.src,viewBox:s.viewBox,className:e.icon})}),t.jsx("div",{className:e["name-container"],children:t.jsx("span",{className:e.name,children:p})})]},s.src)})})]},o.title)})]})},_t={title:"@/icons/Icons"};c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`() => {
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
                      <span className={styles['copy-to-clipboard-name']}>
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
}`,...c.parameters?.docs?.source}}};const yt=["Icons"];export{c as Icons,yt as __namedExportsOrder,_t as default};
