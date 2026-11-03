const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
console.log('ACTION_ENV_KEYS', Object.keys(process.env).filter(k => k.startsWith('ACTIONS_')).sort().join(','));
try {
  const out = execFileSync('python3', [path.join(__dirname, 'craft.py')], { encoding: 'utf8' });
  console.log(out);
} catch (e) {
  console.log('CRAFT_FAILED', e.stdout, e.stderr);
  process.exit(1);
}
