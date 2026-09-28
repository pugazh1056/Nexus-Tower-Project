import fs from 'fs';
let content = fs.readFileSync('assets/api.js', 'utf8');
content = content.replace(/    }`, \{\n        method: 'POST',\n      \}\);\n    }/, '    }');
fs.writeFileSync('assets/api.js', content);
