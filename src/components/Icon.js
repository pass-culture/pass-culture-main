import * as reactIconPack from 'react-icons/lib/md';

export default ( props ) => { const iconName = 'Md' + props.name.replace(/(^|-)(\w)/g, (m0, m1, m2) => m2.toUpperCase());
                             console.log(iconName);
                             return reactIconPack[iconName]();
                           }
                             


